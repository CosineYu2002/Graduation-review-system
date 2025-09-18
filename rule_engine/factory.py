import json
import pandas as pd
from pathlib import Path
from pydantic import TypeAdapter, ValidationError
from typing import Union
from rule_engine.models.rule import Rule
from rule_engine.models.student import Student
from rule_engine.models.course import StudentCourse, BaseCourse


class RuleFactory:
    @staticmethod
    def from_json_file(file_path: Path) -> Rule:
        if not file_path.exists():
            raise FileNotFoundError(f"規則檔案不存在：{file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            json_str = f.read()
        return RuleFactory.from_json_string(json_str)

    @staticmethod
    def from_json_string(json_str: str) -> Rule:
        adapter = TypeAdapter(Rule)
        return adapter.validate_json(json_str)

    @staticmethod
    def from_dict(data: dict) -> Rule:
        adapter = TypeAdapter(Rule)
        return adapter.validate_python(data)


class CourseFactory:
    @staticmethod
    def create_student_course(**kwargs) -> StudentCourse:
        """創建學生課程對象"""
        try:
            return StudentCourse(**kwargs)
        except ValidationError as e:
            raise ValueError(f"無法創建學生課程：{e}")

    @staticmethod
    def create_base_course(**kwargs) -> BaseCourse:
        """創建基礎課程對象"""
        try:
            return BaseCourse(**kwargs)
        except ValidationError as e:
            raise ValueError(f"無法創建基礎課程：{e}")

    @staticmethod
    def from_dict(
        data: dict, course_type: str = "student"
    ) -> Union[StudentCourse, BaseCourse]:
        """從字典創建課程對象"""
        if course_type == "student":
            return CourseFactory.create_student_course(**data)
        else:
            return CourseFactory.create_base_course(**data)

    @staticmethod
    def from_excel_row(row: pd.Series) -> StudentCourse:
        """從 Excel 行數據創建學生課程"""
        course_data = {
            "course_name": row["course_name"],
            "course_codes": (
                [row["course_code"]] if pd.notna(row["course_code"]) else []
            ),
            "credit": float(row["credit"]),
            "grade": int(row["grade"]) if pd.notna(row["grade"]) else 0,
            "category": row.get("category", ""),
            "course_type": int(row.get("course_type", 0)),
            "tag": [],
            "year_taken": int(row.get("year_taken", 2023)),
            "semester_taken": int(row.get("semester_taken", 1)),
            "recognized": False,
        }
        return CourseFactory.create_student_course(**course_data)


class StudentFactory:
    @staticmethod
    def from_json_file(file_path: Path) -> Student:
        if not file_path.exists():
            raise FileNotFoundError(f"學生檔案不存在：{file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            json_str = f.read()
        return StudentFactory.from_json_string(json_str)

    @staticmethod
    def from_json_string(json_str: str) -> Student:
        try:
            adapter = TypeAdapter(Student)
            return adapter.validate_json(json_str)
        except ValidationError as e:
            raise ValueError(f"無法解析學生檔案 JSON：{e}")

    @staticmethod
    def from_dict(data: dict) -> Student:
        try:
            adapter = TypeAdapter(Student)
            return adapter.validate_python(data)
        except ValidationError as e:
            raise ValueError(f"無法解析學生資料：{e}")

    @staticmethod
    def save_student_to_json(student: Student, file_path: Path):
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(student.model_dump(), f, ensure_ascii=False, indent=4)

    @staticmethod
    def create_from_excel_group(
        student_id: str,
        group_data: pd.DataFrame,
        major: str,
    ) -> Student:
        """從 Excel 分組數據創建學生對象"""
        if group_data.empty:
            raise ValueError(f"學生 {student_id} 沒有課程數據")

        student_name = group_data["name"].iloc[0]

        # 創建課程列表
        courses = []
        for _, row in group_data.iterrows():
            try:
                course = CourseFactory.from_excel_row(row)
                courses.append(course)
            except Exception as e:
                print(
                    f"警告：跳過無效課程資料 {row.get('course_name', 'Unknown')}: {e}"
                )
                continue

        student_data = {
            "name": student_name,
            "id": student_id,
            "courses": courses,
            "major": major,
        }

        return StudentFactory.from_dict(student_data)

    @staticmethod
    def load_students_from_excel(
        excel_file_path: Path,
        output_path: Path,
        major: str = "",
    ) -> dict[str, Student]:
        """從 Excel 文件加載學生信息並創建學生對象"""
        if not excel_file_path.exists():
            raise FileNotFoundError(f"Excel 檔案不存在：{excel_file_path}")

        # 讀取 Excel 文件
        try:
            df = pd.read_excel(excel_file_path, engine="openpyxl")
        except Exception as e:
            raise ValueError(f"無法讀取 Excel 檔案：{e}")

        # 標準化列名
        df = df[
            [
                "學號",
                "姓名",
                "課程名稱",
                "課程碼",
                "學分數",
                "成績",
                "承抵課程別",
                "選必修(0,1必修，2選修)",
                "學年",
                "學期",
            ]
        ]
        df.columns = [
            "id",
            "name",
            "course_name",
            "course_code",
            "credit",
            "grade",
            "category",
            "course_type",
            "year_taken",
            "semester_taken",
        ]

        # 清理數據
        df = df.dropna(subset=["id", "name", "course_name"])

        # 按學號分組
        grouped = df.groupby("id")
        students: dict[str, Student] = {}

        for id, group in grouped:
            assert isinstance(id, str)
            try:
                student = StudentFactory.create_from_excel_group(id, group, major)
                students[id] = student

                output_path.mkdir(parents=True, exist_ok=True)
                student_file = output_path / f"{id}.json"
                StudentFactory.save_student_to_json(student, student_file)

            except Exception as e:
                print(f"警告：跳過學生 {id}: {e}")
                continue
        return students

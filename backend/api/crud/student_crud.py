from pathlib import Path

from rule_engine.models.student import Student
from rule_engine.factory import StudentFactory


class StudentCRUD:
    @staticmethod
    def get_all_students() -> list[Student]:
        student_dir = Path("data/students")
        students_info: list[Student] = []

        if not student_dir.exists():
            return []
        json_files = list(student_dir.glob("*.json"))
        for student_file in sorted(json_files):
            try:
                student = StudentFactory.from_json_file(student_file)
                students_info.append(student)
            except Exception as e:
                print(f"警告：跳過檔案 {student_file.name}: {e}")
                continue
        return students_info

    @staticmethod
    def get_student_by_id(student_id: str) -> Student:
        student_dir = Path("data/students")
        student_file = student_dir / f"{student_id}.json"
        if not student_file.exists():
            raise FileNotFoundError(f"找不到學生檔案: {student_file}")
        return StudentFactory.from_json_file(student_file)

    @staticmethod
    def delete_all_students():
        student_dir = Path("data/students")
        if not student_dir.exists():
            return 0

        json_files = list(student_dir.glob("*.json"))
        deleted_count = 0

        for student_file in json_files:
            student_file.unlink()
            deleted_count += 1

        return deleted_count

    @staticmethod
    def delete_student_by_id(student_id: str):
        student_dir = Path("data/students")
        student_file = student_dir / f"{student_id}.json"
        if not student_file.exists():
            raise FileNotFoundError(f"找不到學生檔案: {student_file}")
        student_file.unlink()

import pandas as pd
import json
import os
from rule_updater.generator import RuleGenerator
from rule_engine.models.student import Student
from rule_engine.models.graduation_rule import GraduationRule
from rule_engine.evaluator import Evaluator
from pathlib import Path


def load_student_info(excel_file_path):
    df = pd.read_excel(excel_file_path, engine="openpyxl")
    output_dir = "students"
    os.makedirs(output_dir, exist_ok=True)
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
    ]
    grouped = df.groupby("id")

    for id, group in grouped:
        student_name = group["name"].iloc[0]
        courses = []
        for _, row in group.iterrows():
            courses.append(
                {
                    "course_name": row["course_name"],
                    "course_code": row["course_code"],
                    "credit": float(row["credit"]),
                    "grade": int(row["grade"]),
                    "category": row["category"],
                    "course_type": row["course_type"],
                }
            )

        student_data = {"name": student_name, "id": id, "courses": courses}

        output_path = os.path.join(output_dir, f"{id}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(student_data, f, ensure_ascii=False, indent=4)


def main():
    excel_file_path = "student_info.xlsx"
    load_student_info(excel_file_path)


def add_rule():
    generator = RuleGenerator()
    generator.interactive_mode()


def run_evaluator():
    student_path = Path("students/AN4104765.json")
    student_info = Student.from_json(student_path)
    rule_path = Path("rules/B5/109.json")
    rule_info = GraduationRule.from_json(rule_path)

    evaluator = Evaluator()
    if evaluator.evaluate(rule_info, student_info.courses):
        print("學生符合畢業規則")
    else:
        print("學生不符合畢業規則")


if __name__ == "__main__":
    run_evaluator()

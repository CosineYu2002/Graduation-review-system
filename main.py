import pandas as pd
import json
import os


def load_student_info(excel_file_path):
    df = pd.read_excel(excel_file_path, engine="openpyxl")
    output_dir = "students"
    os.makedirs(output_dir, exist_ok=True)
    df = df[["學號", "姓名", "課程名稱", "課程碼", "學分數", "成績", "承抵課程別"]]
    df.columns = [
        "id",
        "name",
        "course_name",
        "course_code",
        "credit",
        "grade",
        "category",
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
                }
            )

        student_data = {"name": student_name, "id": id, "courses": courses}

        output_path = os.path.join(output_dir, f"{id}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(student_data, f, ensure_ascii=False, indent=4)


def main():
    excel_file_path = "student_info.xlsx"
    load_student_info(excel_file_path)


if __name__ == "__main__":
    main()

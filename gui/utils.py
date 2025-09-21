from typing import Any
import json
from tkinter import ttk

from rule_engine.models.course import StudentCourse


class UtilityFunctions:
    @staticmethod
    def course_to_dict(course) -> dict:
        try:
            if hasattr(course, "model_dump"):
                return course.model_dump()
            if isinstance(course, dict):
                return course
            if hasattr(course, "__dict__"):
                return dict(course.__dict__)
        except Exception:
            pass
        return {}

    @staticmethod
    def get_field_label(course: StudentCourse, key: str) -> str:
        model_fields = getattr(course.__class__, "model_fields", None)
        if model_fields and key in model_fields:
            desc = getattr(model_fields[key], "description", None)
            if desc:
                return str(desc)
        return key

    @staticmethod
    def to_display_value(v: Any) -> str:
        # 友善顯示值
        if v is None:
            return ""
        if isinstance(v, bool):
            return "是" if v else "否"
        if isinstance(v, (list, tuple, set)):
            return "、".join(map(UtilityFunctions.to_display_value, v))
        if isinstance(v, dict):
            try:
                return json.dumps(v, ensure_ascii=False)
            except Exception:
                return str(v)
        return str(v)

    @staticmethod
    def format_grade(val: Any) -> str:
        mapping = {111: "休學", 555: "抵免", 777: "退選", 999: "成績未到"}
        if val is None or val == "":
            return ""
        n: int | None = None
        if isinstance(val, int):
            n = val
        elif isinstance(val, str):
            try:
                n = int(val)
            except ValueError:
                return val
        else:
            return UtilityFunctions.to_display_value(val)

        if n in mapping:
            return mapping[n]
        return str(n)

    @staticmethod
    def extract_course_fields(cd: dict) -> tuple[str, str, str, dict]:
        name = cd.get("course_name") or ""
        code_val = cd.get("course_codes") or ""
        code = UtilityFunctions.to_display_value(code_val)
        score_val = cd.get("grade") or ""
        score = UtilityFunctions.format_grade(score_val)
        details = {
            k: v
            for k, v in cd.items()
            if k
            not in {
                "course_name",
                "course_codes",
                "grade",
                "recognized",
            }
        }
        return str(name), code, score, details

    @staticmethod
    def _populate_course_tree(tree: ttk.Treeview, courses: list) -> None:
        tree.delete(*tree.get_children())
        for c in courses:
            cd = UtilityFunctions.course_to_dict(c)
            name, code, score, details = UtilityFunctions.extract_course_fields(cd)
            iid = tree.insert("", "end", text="", values=(name, code, score))
            # 以子節點展開詳細資料（多行，每項一列）
            for k, v in details.items():
                label = UtilityFunctions.get_field_label(c, k)
                tree.insert(
                    iid,
                    "end",
                    values=(f"  - {label}", UtilityFunctions.to_display_value(v), ""),
                )
        tree.delete(*tree.get_children())
        for c in courses:
            cd = UtilityFunctions.course_to_dict(c)
            name, code, score, details = UtilityFunctions.extract_course_fields(cd)
            iid = tree.insert("", "end", text="", values=(name, code, score))
            # 以子節點展開詳細資料（多行，每項一列）
            for k, v in details.items():
                label = UtilityFunctions.get_field_label(c, k)
                tree.insert(
                    iid,
                    "end",
                    values=(f"  - {label}", UtilityFunctions.to_display_value(v), ""),
                )

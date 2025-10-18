from pathlib import Path
import json
import os
from subprocess import run
from crawler.course_crawler import CourseCrawler


class RuleGenerator:
    def __init__(self):
        self.rule_types = {
            "list_selected": "選修表中課程至少x學分或x門",
            "required": "列表課程皆為必修",
            "prerequisite": "先修課程，要先上完列表中的課程才能繼續上其他課程",
            "corresponding": "對應課程，裡面的課程需要全部都上完才承認",
            "any_selected": "選修任何系上開設選修課至少x學分或x門",
            "final": "最終畢業門檻，每一份規則都需要有一個 final 規則",
        }

    def interactive_mode(self):

        print("歡迎進入規則生成器，請根據指示輸入相關資訊。")
        self._dept_code = input("請輸入系所代碼（例如E2，F7)：")
        while not self._validate_dept_code(self._dept_code):
            print("無效的系所代碼，請重新輸入。")
            self._dept_code = input("請輸入系所代碼（例如E2，F7)：")

        self._admission_year = input("請輸入入學年度（民國，例如110）：")
        while not self._admission_year.isdigit():
            print("入學年請輸入數字")
            self._admission_year = input("請輸入入學年度（民國，例如110）：")
        self._admission_year = int(self._admission_year)

        print(f"正在創建 {self._dept_name} {self._admission_year} 年的輔系畢業規則")
        rules: list[dict] = self._interactive_rule_creation()
        result = {
            "admission_year": self._admission_year,
            "department_code": self._dept_code,
            "rules": rules,
        }
        base_dir = Path(__file__).resolve().parents[1]
        rules_path = (
            base_dir / "rules" / f"{self._dept_code}" / f"{self._admission_year}.json"
        )
        rules_path.parent.mkdir(parents=True, exist_ok=True)
        with open(rules_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

    def _interactive_rule_creation(self) -> list[dict]:
        rules: list[dict] = []
        while True:
            print("可用規則類型：")
            print("0. 退出")
            for i, (rule_type, description) in enumerate(
                self.rule_types.items(), start=1
            ):
                print(f"{i}. {rule_type}: {description}")

            choice = input("請選擇規則類型（輸入數字）：")
            match choice:
                case "0":
                    if not any(rule.get("type") == "final" for rule in rules):
                        (
                            run(["cls"], shell=True)
                            if os.name == "nt"
                            else run(["clear"], shell=True)
                        )
                        print("請至少添加一個 final 規則。")
                        continue
                    (
                        run(["cls"], shell=True)
                        if os.name == "nt"
                        else run(["clear"], shell=True)
                    )
                    print("退出規則創建")
                    return rules
                case "1":  # list_selected
                    rules.append(self._create_list_selected_rule())
                    (
                        run(["cls"], shell=True)
                        if os.name == "nt"
                        else run(["clear"], shell=True)
                    )
                    print("已添加 list_selected 規則")
                case "2":  # required
                    rules.append(self._create_required_rule())
                    (
                        run(["cls"], shell=True)
                        if os.name == "nt"
                        else run(["clear"], shell=True)
                    )
                    print("已添加 required 規則")
                case "3":  # prerequisite
                    rules.append(self._create_prerequisite_rule())
                    (
                        run(["cls"], shell=True)
                        if os.name == "nt"
                        else run(["clear"], shell=True)
                    )
                    print("已添加 prerequisite 規則")
                case "4":  # corresponding
                    rules.append(self._create_corresponding_rule())
                    (
                        run(["cls"], shell=True)
                        if os.name == "nt"
                        else run(["clear"], shell=True)
                    )
                    print("已添加 corresponding 規則")
                case "5":  # any_selected
                    rules.append(self._create_any_selected_rule())
                    (
                        run(["cls"], shell=True)
                        if os.name == "nt"
                        else run(["clear"], shell=True)
                    )
                    print("已添加 any_selected 規則")
                case "6":  # final
                    rules.append(self._create_final_rule())
                    (
                        run(["cls"], shell=True)
                        if os.name == "nt"
                        else run(["clear"], shell=True)
                    )
                    print("已添加 final 規則")
                case _:
                    (
                        run(["cls"], shell=True)
                        if os.name == "nt"
                        else run(["clear"], shell=True)
                    )
                    print("無效的選擇，請重新輸入。")

    def _create_list_selected_rule(self) -> dict:
        print("創建 list_selected 規則")
        description = self._set_description("list_selected")
        min_credits = self._set_min_credits()
        learn_in_dept = self._set_learn_in_dept()
        fallback_department = self._set_fallback_department()
        course_list = self._set_course_list()

        return {
            "type": "list_selected",
            "description": description,
            "min_credits": min_credits,
            "learn_in_dept": learn_in_dept,
            "fallback_department": fallback_department,
            "course_list": course_list,
        }

    def _create_required_rule(self) -> dict:
        print("創建 required 規則")
        description = self._set_description("required")
        learn_in_dept = self._set_learn_in_dept()
        course_list = self._set_course_list()

        return {
            "type": "required",
            "description": description,
            "learn_in_dept": learn_in_dept,
            "course_list": course_list,
        }

    def _create_final_rule(self) -> dict:
        print("創建 final 規則")
        description = self._set_description("final")
        min_credits = self._set_min_credits()

        return {
            "type": "final",
            "description": description,
            "min_credits": min_credits,
        }

    def _create_prerequisite_rule(self) -> dict:
        print("創建 prerequisite 規則")
        description = self._set_description("prerequisite")
        learn_in_dept = self._set_learn_in_dept()
        course_list = self._set_course_list()

        return {
            "type": "prerequisite",
            "description": description,
            "learn_in_dept": learn_in_dept,
            "course_list": course_list,
        }

    def _create_corresponding_rule(self) -> dict:
        print("創建 corresponding 規則")
        description = self._set_description("corresponding")
        learn_in_dept = self._set_learn_in_dept()
        course_list = self._set_course_list()
        return {
            "type": "corresponding",
            "description": description,
            "learn_in_dept": learn_in_dept,
            "course_list": course_list,
        }

    def _create_any_selected_rule(self) -> dict:
        print("創建 any_selected 規則")
        description = self._set_description("any_selected")
        min_course_number = self._set_min_course_number()
        learn_in_dept = self._set_learn_in_dept()

        return {
            "type": "any_selected",
            "description": description,
            "min_course_number": min_course_number,
            "learn_in_dept": learn_in_dept,
        }

    def _set_description(self, rule_type: str) -> str:
        description = input("請輸入描述（可留空）：")
        if not description.strip():
            description = self.rule_types[rule_type]
        return description

    def _set_min_credits(self) -> float:
        min_credits = input("請輸入最少學分數（例如：18）：")
        while not min_credits.isdigit() or float(min_credits) <= 0:
            print("學分數必須是正整數，請重新輸入。")
            min_credits = input("請輸入最少學分數：")
        return float(min_credits)

    def _set_learn_in_dept(self) -> bool:
        learn_in_dept_str = input("是否只限於本系所課程？(y/n)：").strip().lower()
        while learn_in_dept_str not in ["y", "n"]:
            print("無效的選擇，請重新輸入。")
            learn_in_dept_str = input("是否只限於本系所課程？：").strip().lower()
        if learn_in_dept_str == "y":
            return True
        else:
            return False

    def _set_fallback_department(self) -> list[str]:
        while True:
            fallback_department_ans = input(
                "備選系所代碼（可留空，若有兩個以上，代碼之間留空）："
            )
            if not fallback_department_ans.strip():
                return []
            else:
                fallback_department = fallback_department_ans.split()
                error = []
                for dept in fallback_department:
                    if not self._validate_dept_code(dept):
                        error.append(dept)
                if not error:
                    return fallback_department
                else:
                    print(f"無效的系所代碼：{', '.join(error)}，請重新輸入。")

    def _set_course_list(self) -> list[dict]:
        base_path = Path(__file__).resolve().parents[1]
        target_path = base_path / "data" / "course_list.json"
        if not target_path.exists():
            raise FileNotFoundError(f"課程列表檔案不存在: {target_path}")

        course_list_str = json.loads(target_path.read_text(encoding="utf-8"))
        return CourseCrawler(self._dept_code, course_list_str).run()

    def _set_min_course_number(self) -> int:
        min_course_number = input("請輸入最少課程數量（例如：3）：")
        while not min_course_number.isdigit() or int(min_course_number) <= 0:
            print("課程數量必須是正整數，請重新輸入。")
            min_course_number = input("請輸入最少課程數量：")
        return int(min_course_number)

    def _load_departments_info(self) -> dict[str, dict[str, str]]:
        base_dir = Path(__file__).resolve().parents[1]
        data_path = base_dir / "data" / "departments_info.json"
        if not data_path.exists():
            raise FileNotFoundError(f"系所資料檔案不存在: {data_path}")

        try:
            return json.loads(data_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            raise ValueError(f"無效的JSON格式: {data_path}")

    def _validate_dept_code(self, dept_code: str) -> bool:
        data = self._load_departments_info()

        if dept_code in data.keys():
            self._dept_name = data[dept_code]["name_zh_tw"]
            return True
        else:
            return False

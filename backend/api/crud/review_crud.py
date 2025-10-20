from pathlib import Path
from rule_engine.models.student import Student
from rule_engine.models.rule import Rule, RuleSet
from rule_engine.models.result import Result
from rule_engine.evaluator import Evaluator
from rule_engine.factory import RuleFactory
from rule_engine.utils import UtilFunctions


class ReviewCRUD:
    @staticmethod
    def select_rule(
        department: str, admission_year: int, rule_type: str
    ) -> Rule | None:
        """
        選擇規則

        Args:
            department: 科系代號
            admission_year: 入學年度
            rule_type: "minor" 或 "double_major" 或 "major"

        Returns:
            Rule 或是 None
        """
        rules_dir = Path("data/rules")

        if not rules_dir.exists():
            raise FileNotFoundError(f"規則目錄不存在：{rules_dir}")

        dept_dir = rules_dir / department
        if not dept_dir.exists():
            raise FileNotFoundError(f"找不到科系 '{department}' 對應的規則資料夾")

        # 根據類型設定後綴
        suffix = f"_{rule_type}"

        # 尋找符合條件的規則文件
        rule_files = list(dept_dir.glob(f"*{suffix}.json"))
        if not rule_files:
            raise FileNotFoundError(
                f"科系 '{department}' 沒有可用的 {rule_type} 規則文件"
            )

        # 解析文件名稱中的年度
        eligible_rules = []

        for rule_file in rule_files:
            filename = rule_file.stem  # 去除副檔名
            # 移除後綴
            year_part = filename.replace(suffix, "")

            # 檢查是否為純數字
            if year_part.isdigit():
                rule_year = int(year_part)
                if rule_year <= admission_year:
                    eligible_rules.append((rule_year, rule_file))

        if not eligible_rules:
            raise FileNotFoundError(
                f"找不到適用於入學年度 {admission_year} 的 {rule_type} 規則"
            )

        # 選擇最大但小於等於入學年度的規則
        eligible_rules.sort(key=lambda x: x[0], reverse=True)
        _, selected_rule_file = eligible_rules[0]

        # 載入規則
        rule = RuleFactory.from_json_file(selected_rule_file)

        return rule

    @staticmethod
    def perform_evaluation(student: Student, rule: Rule) -> Result:
        """
        執行畢業審查評估

        Args:
            student: 學生資料
            rule: 審查規則

        Returns:
            Result: 審查結果
        """
        evaluator = Evaluator()
        result = evaluator.evaluate(rule, student.courses)
        return result

    @staticmethod
    def save_evaluation_result(student: Student, results: dict[str, Result | None]):
        output_dir = Path("data/evaluation_results")
        output_dir.mkdir(exist_ok=True)
        from datetime import datetime

        now = datetime.now()
        result_file = output_dir / f"{student.id}_{now.strftime("%d_%b_%Y_%H_%M")}.json"
        result_data = student.model_dump(exclude={"courses"})
        result_data |= {
            key: model.model_dump() if model else None for key, model in results.items()
        }
        import json

        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def review_student(
        student: Student,
        major_department: str | None = None,
        double_major_department: str | None = None,
        minor_departments: list[str] | None = None,
    ) -> dict[str, Result | None]:
        """
        對學生進行完整的畢業審查

        Args:
            student: 學生資料
            major_department: 主修科系（若為 None 則使用學生本身的科系）
            double_major_department: 雙主修科系
            minor_departments: 輔系科系列表

        Returns:
            dict[str, Result]: 包含各項審查結果的字典
                - "main": 主修審查結果
                - "double_major": 雙主修審查結果（如果有）
                - "minor_<dept>": 各輔系審查結果（如果有）
        """
        results: dict[str, Result | None] = {}

        # 1. 主修系
        review_dept = major_department if major_department else student.major

        # 載入主修規則
        main_rule = ReviewCRUD.select_rule(review_dept, student.admission_year, "major")

        # 如果主修是不分系，判斷有沒有輔系(minor)
        if review_dept == "AN":
            if not minor_departments or len(minor_departments) == 0:
                raise ValueError(
                    "不分系學生 (AN) 必須提供至少一個輔系 (minor_departments) 以進行審查"
                )

            # 取得專長系的科系代碼
            dept_codes_in_college = UtilFunctions().get_department_code(
                minor_departments[0]
            )

            # 調整規則
            if isinstance(main_rule, RuleSet):
                # 調整第一個子規則：某系輔修
                selected_info = ReviewCRUD.select_rule(
                    minor_departments[0], student.admission_year, "minor"
                )
                if selected_info:
                    main_rule.sub_rules[0] = selected_info

                    # 調整其他子規則中的科系代碼
                    from rule_engine.models.rule import RuleAll

                    for sub_rule in main_rule.sub_rules[1:]:
                        if isinstance(sub_rule, RuleAll):
                            sub_rule.course_criteria.department_codes = (
                                dept_codes_in_college
                            )

            minor_departments.pop(0)
            if len(minor_departments) == 0:
                minor_departments = None

        # 確保 main_rule 不為 None
        if main_rule is None:
            raise ValueError(
                f"無法為科系 '{review_dept}' 和入學年度 {student.admission_year} 找到適用的規則"
            )

        # 執行主修審查
        results["main"] = ReviewCRUD.perform_evaluation(student, main_rule)

        # 2. 雙主修審查
        if double_major_department:
            try:
                double_major_rule = ReviewCRUD.select_rule(
                    double_major_department, student.admission_year, "double_major"
                )
                if double_major_rule:
                    results[f"double_major_{double_major_department}"] = (
                        ReviewCRUD.perform_evaluation(student, double_major_rule)
                    )
            except FileNotFoundError as e:
                # 如果找不到雙主修規則，記錄錯誤但繼續
                results["double_major_error"] = None

        # 3. 輔系審查
        if minor_departments:
            for minor_dept in minor_departments:
                try:
                    minor_rule = ReviewCRUD.select_rule(
                        minor_dept, student.admission_year, "minor"
                    )
                    if minor_rule:
                        results[f"minor_{minor_dept}"] = ReviewCRUD.perform_evaluation(
                            student, minor_rule
                        )
                except FileNotFoundError as e:
                    # 如果找不到輔系規則，記錄錯誤但繼續
                    results[f"minor_{minor_dept}_error"] = None

        ReviewCRUD.save_evaluation_result(student, results)

        return results

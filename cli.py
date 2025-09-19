import os
import sys
import json
from pathlib import Path
from datetime import datetime
from rule_engine.factory import StudentFactory, RuleFactory
from rule_engine.evaluator import Evaluator
from rule_engine.utils import UtilFunctions
from rule_engine.models.student import Student
from rule_engine.models.rule import *
from rule_engine.models.result import Result


class GraduationSystemCLI:
    def __init__(self):
        self.students: dict[str, Student] = {}
        self.evaluator = Evaluator()
        self.students_dir = Path("students")
        self.rules_dir = Path("rules")

    def clear_screen(self):
        """清屏"""
        os.system("cls" if os.name == "nt" else "clear")

    def print_banner(self):
        """打印欢迎横幅"""
        print("=" * 60)
        print("              畢業審查系統 CLI")
        print("=" * 60)
        print()

    def print_menu(self):
        """打印主菜单"""
        menu_items = [
            "1. 從 Excel 載入學生資料",
            "2. 載入已存在的學生資料",
            "3. 查看已載入的學生列表",
            "4. 選擇學生進行畢業審查",
            "5. 退出系統",
        ]

        print("請選擇操作：")
        for item in menu_items:
            print(f"  {item}")
        print()

    def load_students_from_excel_interactive(self):
        """交互式從 Excel 載入學生資料"""
        print("\n--- 從 Excel 載入學生資料 ---")

        # 輸入 Excel 文件路徑
        excel_path = input("請輸入 Excel 文件路徑：").strip()
        if not excel_path:
            excel_path = "student_info.xlsx"

        input_path = Path(excel_path)
        if not input_path.exists():
            print(f"❌ 文件不存在：{excel_path}")
            return

        # 輸入主修科系
        major: str = ""
        while not major:
            major = input("請輸入主修科系代號（例如，不分系請輸入AN）：").strip()

        # 確保輸出目錄存在
        output_path = Path("students")
        output_path.mkdir(parents=True, exist_ok=True)

        try:
            print("正在載入學生資料...")
            self.students = StudentFactory.load_students_from_excel(
                input_path, output_path, major
            )
            print(f"✅ 學生資料載入完成，共載入 {len(self.students)} 位學生")
        except Exception as e:
            print(f"❌ 載入失敗：{e}")

    def load_existing_students(self):
        """載入已存在的學生資料"""
        print("\n--- 載入已存在的學生資料 ---")

        if not self.students_dir.exists():
            self.students_dir.mkdir(parents=True, exist_ok=True)

        json_files = list(self.students_dir.glob("*.json"))
        if not json_files:
            print("❌ 沒有找到學生資料文件")
            return

        try:
            for json_file in json_files:
                student = StudentFactory.from_json_file(json_file)
                self.students[student.id] = student
            print(f"✅ 成功載入 {len(self.students)} 位學生")
        except Exception as e:
            print(f"❌ 載入失敗：{e}")

    def select_student_for_evaluation(self):
        """選擇學生進行畢業審查"""
        if not self.students:
            print("❌ 請先載入學生資料")
            return

        print("\n--- 選擇學生進行畢業審查 ---")

        # 顯示學生列表
        self.show_loaded_students()

        # 選擇學生
        while True:
            student_id = (
                input("請輸入學生學號（或輸入 'back' 返回主菜單）：").strip().upper()
            )

            if student_id.lower() == "back":
                return

            if student_id in self.students:
                selected_student = self.students[student_id]
                break
            else:
                print(f"❌ 找不到學號為 {student_id} 的學生，請重新輸入")

        # 選擇規則
        rule = self.auto_select_rule(selected_student)
        if not rule:
            return

        if selected_student.major == "AN":
            print("⚠️  注意：學生主修為不分系，請選擇專長系")
            selected_info = self.select_minor_rule()
            assert isinstance(rule, RuleSet)
            if selected_info:
                rule.sub_rules[0] = selected_info[0]
                for sub_rule in rule.sub_rules[1:]:
                    assert isinstance(sub_rule, RuleAll)
                    sub_rule.course_criteria.department_codes = selected_info[1]

        # 執行評估
        self.perform_evaluation(selected_student, rule)

    def auto_select_rule(self, student: Student) -> Rule | None:
        print(f"\n--- 自動選擇畢業規則 ---")
        print(f"學生主修：{student.major}")
        print(f"入學年度：{student.admission_year}")

        if not self.rules_dir.exists():
            print(f"❌ 規則目錄不存在：{self.rules_dir}")
            return None

        # 檢查主修科系對應的資料夾
        dept_dir = self.rules_dir / student.major
        if not dept_dir.exists():
            print(f"❌ 找不到主修科系 '{student.major}' 對應的規則資料夾")
            return None

        # 尋找該科系的所有規則文件
        rule_files = list(dept_dir.glob("*.json"))
        if not rule_files:
            print(f"❌ 科系 '{student.major}' 沒有可用的規則文件")
            return None

        # 解析文件名稱中的年度，並找到符合條件的最大年度
        eligible_rules = []

        for rule_file in rule_files:
            filename = rule_file.stem  # 去除副檔名

            # 檢查是否為純數字（不包含底線、字母等特殊字符）
            if filename.isdigit():
                rule_year = int(filename)
                if rule_year <= student.admission_year:
                    eligible_rules.append((rule_year, rule_file))
                    print(f"✓ 找到符合條件的規則：{filename}.json (年度: {rule_year})")

        if not eligible_rules:
            print(f"❌ 找不到適用於入學年度 {student.admission_year} 的規則")
            return None

        # 選擇最大但小於等於入學年度的規則
        eligible_rules.sort(key=lambda x: x[0], reverse=True)
        selected_year, selected_rule_file = eligible_rules[0]

        print(f"✅ 自動選擇規則：{selected_rule_file.name} (適用年度: {selected_year})")

        # 載入規則
        try:
            rule = RuleFactory.from_json_file(selected_rule_file)
            print(f"✅ 成功載入規則：{rule.name}")
            return rule

        except Exception as e:
            print(f"❌ 載入規則失敗：{e}")
            return None

    def show_loaded_students(self):
        """顯示已載入的學生列表"""
        if not self.students:
            print("❌ 尚未載入任何學生資料")
            return

        print("\n已載入的學生列表：")
        print("-" * 40)
        print(f"{'學號':<15} {'姓名':<20} {'主修科系':<10}")
        print("-" * 40)
        for student in self.students.values():
            print(f"{student.id:<15} {student.name:<20} {student.major:<10}")
        print("-" * 40)

    def select_minor_rule(self) -> tuple[Rule, list[str]] | None:
        """選擇畢業規則"""
        print("\n--- 選擇輔系畢業規則 ---")

        if not self.rules_dir.exists():
            print(f"❌ 規則目錄不存在：{self.rules_dir}")
            return None

        # 尋找所有規則文件
        rule_files = []
        for dept_dir in self.rules_dir.iterdir():
            if dept_dir.is_dir():
                for rule_file in dept_dir.glob("*.json"):
                    if "_" in rule_file.stem:
                        rule_files.append(rule_file)

        if not rule_files:
            print("❌ 沒有找到規則文件")
            return None

        # 顯示規則選項
        print("可用的畢業規則：")
        for i, rule_file in enumerate(rule_files, 1):
            dept_code = rule_file.parent.name
            year = rule_file.stem
            print(f"  {i}. {dept_code} - {year}")
        print()

        # 選擇規則
        while True:
            try:
                choice = input("請選擇規則編號（或輸入 'back' 返回）：").strip()

                if choice.lower() == "back":
                    return None

                rule_index = int(choice) - 1
                if 0 <= rule_index < len(rule_files):
                    selected_rule_file = rule_files[rule_index]
                    break
                else:
                    print("❌ 無效的選擇，請重新輸入")

            except ValueError:
                print("❌ 請輸入有效的數字")

        # 載入規則
        try:
            rule = RuleFactory.from_json_file(selected_rule_file)
            dept_code = selected_rule_file.parent.name
            dept_codes_in_college = UtilFunctions().get_department_code(dept_code)
            print(f"✅ 成功載入規則：{selected_rule_file}")
            return (rule, dept_codes_in_college)

        except Exception as e:
            print(f"❌ 載入規則失敗：{e}")
            return None

    def perform_evaluation(self, student: Student, rule: Rule):
        """執行畢業審查評估"""
        print(f"\n--- 執行畢業審查 ---")
        print(f"學生：{student.name} ({student.id})")
        print(f"規則：{rule.name}")
        print()

        try:
            # 執行評估
            print("正在進行畢業審查...")
            result = self.evaluator.evaluate(rule, student.courses)

            # 顯示結果
            self.display_evaluation_result(student, rule, result)

            # 詢問是否保存結果
            save_choice = input("\n是否保存審查結果？(y/n)：").strip().lower()
            if save_choice == "y":
                self.save_evaluation_result(student, rule, result)

        except Exception as e:
            print(f"❌ 評估過程中發生錯誤：{e}")

    def display_evaluation_result(self, student: Student, rule: Rule, result: Result):
        """顯示評估結果"""
        print("\n" + "=" * 60)
        print("                畢業審查結果")
        print("=" * 60)

        print(f"學生姓名：{student.name}")
        print(f"學    號：{student.id}")
        print(f"主修科系：{student.major}")
        print(f"審查規則：{rule.name}")
        print()

        # 總體結果
        if result.is_valid:
            print("🎉 審查結果：通過")
        else:
            print("❌ 審查結果：不通過")

        print(f"獲得學分：{result.earned_credits}")
        print()

    def save_evaluation_result(self, student: Student, rule: Rule, result: Result):
        """保存評估結果"""
        try:
            output_dir = Path("evaluation_results")
            output_dir.mkdir(exist_ok=True)

            result_file = (
                output_dir / f"{student.id}_{rule.name.replace(' ', '_')}_result.json"
            )

            result_data = {
                "student": student.model_dump(exclude={"courses"}),
                "result": result.model_dump(),
                "evaluation_time": str(datetime.now()),
            }

            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(result_data, f, ensure_ascii=False, indent=4)

            print(f"✅ 結果已保存至：{result_file}")

        except Exception as e:
            print(f"❌ 保存結果失敗：{e}")

    def run(self):
        """運行 CLI 界面"""
        while True:
            self.clear_screen()
            self.print_banner()
            self.print_menu()

            choice = input("請輸入選項 (1-5)：").strip()

            if choice == "1":
                self.load_students_from_excel_interactive()
            elif choice == "2":
                self.load_existing_students()
            elif choice == "3":
                self.show_loaded_students()
            elif choice == "4":
                self.select_student_for_evaluation()
            elif choice == "5":
                print("👋 感謝使用畢業審查系統！")
                sys.exit(0)
            else:
                print("❌ 無效的選項，請重新選擇")

            input("\n按 Enter 繼續...")

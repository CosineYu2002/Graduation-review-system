from pathlib import Path
import json
from typing import ClassVar
import re

from api.models.rule_models import *
from rule_engine.factory import RuleFactory


class RuleCRUD:
    """規則資料的 CRUD 操作"""

    RULE_FILE_NAME_PATTERN: ClassVar[str] = r"^(\d{2,3})_(minor|double_major|major)$"

    @staticmethod
    def _load_departments_info() -> dict[str, dict[str, str]]:
        """載入系所資訊"""
        dept_file = Path("data/departments_info.json")
        if not dept_file.exists():
            return {}

        with open(dept_file, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _get_department_name(
        dept_code: str, departments_info: dict[str, dict[str, str]]
    ) -> tuple[str, str]:
        """
        取得系所名稱和學院

        Returns:
            tuple[str, str]: (系所名稱, 學院名稱)
        """
        dept_info = departments_info.get(dept_code, {})
        dept_name = dept_info.get("name_zh_tw", dept_code)
        college = dept_info.get("college", "未知學院")
        return dept_name, college

    @staticmethod
    def _parse_rule_file_name(file_name: str) -> tuple[RuleTypeEnum, int]:
        match = re.match(RuleCRUD.RULE_FILE_NAME_PATTERN, file_name)
        if not match:
            raise ValueError(f"無法解析檔名中的規則類型: {file_name}")
        admission_year = int(match.group(1))
        suffix = match.group(2)
        match suffix:
            case "minor":
                return RuleTypeEnum.MINOR, admission_year
            case "double_major":
                return RuleTypeEnum.DOUBLE_MAJOR, admission_year
            case "major":
                return RuleTypeEnum.MAJOR, admission_year
            case _:
                raise ValueError(f"未知的規則類型後綴: {suffix}")

    @staticmethod
    def get_all_rules() -> list[RuleBasicInfo]:
        """
        取得所有規則的基本資訊

        Returns:
            list[RuleBasicInfo]: 規則列表，包含系所名稱和適用年份
        """
        rules_dir = Path("data/rules")
        if not rules_dir.exists():
            return []

        departments_info = RuleCRUD._load_departments_info()
        rules_list: list[RuleBasicInfo] = []

        # 遍歷所有系所目錄
        for dept_dir in sorted(rules_dir.iterdir()):
            if not dept_dir.is_dir():
                continue

            dept_code = dept_dir.name
            dept_name, college = RuleCRUD._get_department_name(
                dept_code, departments_info
            )

            # 遍歷該系所的所有規則檔案
            for rule_file in sorted(dept_dir.glob("*.json")):
                try:
                    rule_type, admission_year = RuleCRUD._parse_rule_file_name(
                        rule_file.stem
                    )

                    rules_list.append(
                        RuleBasicInfo(
                            department_code=dept_code,
                            department_name=dept_name,
                            admission_year=admission_year,
                            college=college,
                            rule_type=rule_type,
                        )
                    )
                except (ValueError, json.JSONDecodeError) as e:
                    print(f"警告：跳過檔案 {rule_file.name}: {e}")
                    continue

        return rules_list

    @staticmethod
    def get_rule_detail(
        department_code: str, admission_year: int, rule_type: RuleTypeEnum
    ) -> RuleDetail | None:
        """
        取得特定規則的詳細資訊

        Args:
            department_code: 系所代碼
            admission_year: 入學年度
            is_minor: 是否為輔系規則

        Returns:
            RuleDetail: 規則詳細資訊，如果不存在則返回 None
        """
        # 構建檔案路徑
        filename = f"{admission_year}_{rule_type.value}.json"
        rule_file = Path("data/rules") / department_code / filename

        if not rule_file.exists():
            return None

        try:
            rule_content = RuleFactory.from_json_file(rule_file)

            # 載入系所資訊
            departments_info = RuleCRUD._load_departments_info()
            dept_name, college = RuleCRUD._get_department_name(
                department_code, departments_info
            )
            return RuleDetail(
                basic_info=RuleBasicInfo(
                    department_code=department_code,
                    department_name=dept_name,
                    admission_year=admission_year,
                    college=college,
                    rule_type=rule_type,
                ),
                rule_content=rule_content,
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"錯誤：無法解析規則檔案 {rule_file}: {e}")
            return None

    @staticmethod
    def create_rule(request: CreateRuleRequest) -> RuleBasicInfo:
        # 檢查系所是否存在
        departments_info = RuleCRUD._load_departments_info()
        if request.department_code not in departments_info:
            raise ValueError(f"系所代碼 {request.department_code} 不存在")

        # 確保目錄存在
        dept_dir = Path("data/rules") / request.department_code
        dept_dir.mkdir(parents=True, exist_ok=True)

        # 構建檔案路徑
        filename = f"{request.admission_year}_{request.rule_type.value}.json"
        rule_file = dept_dir / filename

        if rule_file.exists():
            raise FileExistsError(
                f"{request.department_code} {request.admission_year} 學年度 {request.rule_type.value} 規則已存在"
            )

        # 寫入檔案
        with open(rule_file, "w", encoding="utf-8") as f:
            json.dump(
                request.rule_content.model_dump(), f, ensure_ascii=False, indent=4
            )

        return RuleBasicInfo(
            department_code=request.department_code,
            department_name=departments_info[request.department_code]["name_zh_tw"],
            admission_year=request.admission_year,
            college=departments_info[request.department_code]["college"],
            rule_type=request.rule_type,
        )

    @staticmethod
    def update_rule(request: CreateRuleRequest) -> RuleBasicInfo:
        """
        更新規則

        Args:
            request: 更新規則請求

        Returns:
            RuleBasicInfo: 更新後的規則基本資訊

        Raises:
            ValueError: 系所代碼不存在
            FileNotFoundError: 規則不存在
        """
        # 檢查系所是否存在
        departments_info = RuleCRUD._load_departments_info()
        if request.department_code not in departments_info:
            raise ValueError(f"系所代碼 {request.department_code} 不存在")

        # 構建檔案路徑
        dept_dir = Path("data/rules") / request.department_code
        filename = f"{request.admission_year}_{request.rule_type.value}.json"
        rule_file = dept_dir / filename

        if not rule_file.exists():
            raise FileNotFoundError(
                f"{request.department_code} {request.admission_year} 學年度 {request.rule_type.value} 規則不存在"
            )

        # 更新檔案
        with open(rule_file, "w", encoding="utf-8") as f:
            json.dump(
                request.rule_content.model_dump(), f, ensure_ascii=False, indent=4
            )

        return RuleBasicInfo(
            department_code=request.department_code,
            department_name=departments_info[request.department_code]["name_zh_tw"],
            admission_year=request.admission_year,
            college=departments_info[request.department_code]["college"],
            rule_type=request.rule_type,
        )

    @staticmethod
    def delete_rule(
        department_code: str, admission_year: int, rule_type: RuleTypeEnum
    ) -> bool:
        """
        刪除規則

        Args:
            department_code: 系所代碼
            admission_year: 入學年度
            is_minor: 是否為輔系規則

        Returns:
            bool: 是否成功刪除
        """
        filename = f"{admission_year}_{rule_type.value}.json"
        rule_file = Path("data/rules") / department_code / filename

        if not rule_file.exists():
            return False

        rule_file.unlink()
        return True

    @staticmethod
    def get_departments() -> dict[str, dict]:
        """
        取得所有系所資訊

        Returns:
            dict: 系所代碼到系所資訊的映射
        """
        return RuleCRUD._load_departments_info()

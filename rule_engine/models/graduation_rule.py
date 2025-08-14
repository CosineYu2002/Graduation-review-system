from __future__ import annotations
from dataclasses import dataclass, field
from rule_engine.models.rule import BaseRule
from pathlib import Path
import json


@dataclass
class GraduationRule:
    admission_year: int
    department_code: str
    rules: list[BaseRule] = field(default_factory=list)

    @classmethod
    def from_dict(cls, year_data: dict) -> GraduationRule:
        rules = [
            BaseRule.from_dict(rule_data) for rule_data in year_data.get("rules", [])
        ]
        rules.sort(key=lambda rule: rule.priority, reverse=True)

        return cls(
            admission_year=year_data["admission_year"],
            department_code=year_data["department_code"],
            rules=rules,
        )

    @classmethod
    def from_json(cls, json_file_path: Path) -> GraduationRule:
        if not json_file_path.exists():
            raise FileNotFoundError(f"找不到規則檔案: {json_file_path}")

        try:
            data = json.loads(json_file_path.read_text(encoding="utf-8"))
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"錯誤的 JSON 格式：{e}，路徑：{json_file_path}")
        except Exception as e:
            raise RuntimeError(f"讀取規則檔案時發生錯誤：{e}，路徑：{json_file_path}")

from __future__ import annotations
from dataclasses import dataclass, field
from rule_engine.models.course import Course


@dataclass
class BaseRule:
    type: str
    description: str

    def __post_init__(self):
        if not self.type:
            raise ValueError("規則類型不能為空")
        if not self.description:
            raise ValueError("規則描述不能為空")

    @classmethod
    def from_dict(cls, rule_data: dict) -> BaseRule:
        rule_type = rule_data.get("type")
        match rule_type:
            case "list_selected":
                return ListSelectedRule.from_dict(rule_data)
            case "required":
                return RequiredRule.from_dict(rule_data)
            case "prerequisite":
                return PrerequisiteRule.from_dict(rule_data)
            case "corresponding":
                return CorrespondingRule.from_dict(rule_data)
            case "any_selected":
                return AnySelectedRule.from_dict(rule_data)
            case "final":
                return FinalRule.from_dict(rule_data)
            case _:
                raise ValueError(f"未知的規則類型: {rule_type}")

    @classmethod
    def _create_course_list(cls, course_data) -> list[Course]:
        courses = []
        for course_dict in course_data:
            course = Course(
                course_name=course_dict["name"],
                credits=course_dict["credits"],
                course_codes=course_dict["course_codes"],
            )
            courses.append(course)
        return courses


@dataclass
class ListSelectedRule(BaseRule):
    min_credits: float | None
    min_course_number: int | None
    learn_in_dept: bool
    fallback_department: list[str] = field(default_factory=list)
    course_list: list[Course] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        if self.min_credits is not None and self.min_course_number is not None:
            raise ValueError("不能同時設定最少學分數和最少課程數量")
        elif self.min_credits is None and self.min_course_number is None:
            raise ValueError("至少需要設定最少學分數或最少課程數量")

        if self.min_credits is not None and self.min_credits < 0:
            raise ValueError("最少學分數需大於0")

        if self.min_course_number is not None and self.min_course_number < 0:
            raise ValueError("最少課程數量需大於0")

        if not self.course_list:
            raise ValueError("課程列表不能為空")

    @classmethod
    def from_dict(cls, rule_data: dict) -> ListSelectedRule:
        return cls(
            type=rule_data["type"],
            description=rule_data["description"],
            min_credits=rule_data.get("min_credits"),
            min_course_number=rule_data.get("min_course_number"),
            learn_in_dept=rule_data["learn_in_dept"],
            fallback_department=rule_data.get("fallback_department", []),
            course_list=cls._create_course_list(rule_data["course_list"]),
        )


@dataclass
class RequiredRule(BaseRule):
    learn_in_dept: bool
    course_list: list[Course] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        if not self.course_list:
            raise ValueError("必修課程列表不能為空")

    @classmethod
    def from_dict(cls, rule_data: dict) -> RequiredRule:
        return cls(
            type=rule_data["type"],
            description=rule_data["description"],
            learn_in_dept=rule_data["learn_in_dept"],
            course_list=cls._create_course_list(rule_data["course_list"]),
        )


@dataclass
class PrerequisiteRule(BaseRule):
    learn_in_dept: bool
    course_list: list[Course] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        if not self.course_list:
            raise ValueError("先修課程列表不能為空")

    @classmethod
    def from_dict(cls, rule_data: dict) -> PrerequisiteRule:
        return cls(
            type=rule_data["type"],
            description=rule_data["description"],
            learn_in_dept=rule_data["learn_in_dept"],
            course_list=cls._create_course_list(rule_data["course_list"]),
        )


@dataclass
class CorrespondingRule(BaseRule):
    learn_in_dept: bool
    course_list: list[Course] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        if not self.course_list:
            raise ValueError("對應課程列表不能為空")

    @classmethod
    def from_dict(cls, rule_data: dict) -> CorrespondingRule:
        return CorrespondingRule(
            type=rule_data["type"],
            description=rule_data["description"],
            learn_in_dept=rule_data["learn_in_dept"],
            course_list=cls._create_course_list(rule_data["course_list"]),
        )


@dataclass
class AnySelectedRule(BaseRule):
    learn_in_dept: bool
    min_credits: float | None
    min_course_number: int | None

    def __post_init__(self):
        super().__post_init__()
        if self.min_credits is not None and self.min_course_number is not None:
            raise ValueError("不能同時設定最少學分數和最少課程數量")
        elif self.min_credits is None and self.min_course_number is None:
            raise ValueError("至少需要設定最少學分數或最少課程數量")

        if self.min_credits is not None and self.min_credits < 0:
            raise ValueError("最少學分數需大於0")
        if self.min_course_number is not None and self.min_course_number < 0:
            raise ValueError("最少課程數量需大於0")

    @classmethod
    def from_dict(cls, rule_data: dict) -> AnySelectedRule:
        return cls(
            type=rule_data["type"],
            description=rule_data["description"],
            learn_in_dept=rule_data["learn_in_dept"],
            min_credits=rule_data.get("min_credits"),
            min_course_number=rule_data.get("min_course_number"),
        )


@dataclass
class FinalRule(BaseRule):
    min_credits: float

    def __post_init__(self):
        super().__post_init__()
        if self.min_credits <= 0:
            raise ValueError("最少學分數需大於0")

    @classmethod
    def from_dict(cls, rule_data: dict) -> FinalRule:
        return cls(
            type=rule_data["type"],
            description=rule_data["description"],
            min_credits=rule_data["min_credits"],
        )

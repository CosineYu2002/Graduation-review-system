from .models.course import Course, StudentCourse
from .models.student import StudentType
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class MatchMode(Enum):
    NAME = "name"
    CODE = "code"
    BOTH = "both"
    EITHER = "either"


class MatchConfig(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    mode: MatchMode = Field(default=MatchMode.BOTH, description="匹配模式")
    learn_in_dept: bool = Field(default=True, description="是否僅限於系所課程")
    dept_code: str = Field(default="", description="學生系所代碼")
    substitute_dept_codes: list[str] | None = Field(
        default=None, description="如果承認外系課程，則填寫系所代碼"
    )
    course_types: frozenset[int] = Field(
        default_factory=frozenset, description="可接受的選必修類別"
    )
    categories: frozenset[str] = Field(
        default_factory=frozenset, description="可接受的承抵課程類別"
    )


class CourseMatcher:
    @staticmethod
    def match(
        student_course: StudentCourse, course: Course, config: MatchConfig
    ) -> bool:
        if config.learn_in_dept:
            if not student_course.course_code.startswith(config.dept_code):
                return False

        if config.substitute_dept_codes:
            if not any(
                student_course.course_code.startswith(dept_code)
                for dept_code in (config.substitute_dept_codes or [])
            ) and not student_course.course_code.startswith(config.dept_code):
                return False

        if (
            config.course_types
            and student_course.course_type not in config.course_types
        ):
            return False

        if config.categories and student_course.category not in config.categories:
            return False

        return _MATCH_STRATEGIES[config.mode](student_course, course)


_MATCH_STRATEGIES = {
    MatchMode.NAME: lambda sc, c: sc.course_name == c.course_name,
    MatchMode.CODE: lambda sc, c: sc.course_code in c.course_codes,
    MatchMode.BOTH: lambda sc, c: sc.course_name == c.course_name
    and sc.course_code in c.course_codes,
    MatchMode.EITHER: lambda sc, c: sc.course_name == c.course_name
    or sc.course_code in c.course_codes,
}

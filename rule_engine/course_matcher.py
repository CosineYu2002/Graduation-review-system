from .models.course import Course, StudentCourse
from enum import Enum
from dataclasses import dataclass


class MatchMode(Enum):
    NAME = "name"
    CODE = "code"
    BOTH = "both"
    EITHER = "either"


@dataclass(frozen=True, slots=True)
class MatchConfig:
    mode: MatchMode = MatchMode.BOTH
    dept_only: bool = False
    dept_code: str | None = None
    course_types: frozenset[int] = frozenset()
    categories: frozenset[str] = frozenset()


class CourseMatcher:
    STRICT = MatchConfig(MatchMode.BOTH)
    NAME_ONLY = MatchConfig(MatchMode.NAME)
    CODE_ONLY = MatchConfig(MatchMode.CODE)
    EITHER = MatchConfig(MatchMode.EITHER)

    @staticmethod
    def match(
        student_course: StudentCourse, course: Course, config: MatchConfig
    ) -> bool:
        if config.dept_only and config.dept_code:
            if not student_course.course_code.startswith(config.dept_code):
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
    MatchMode.CODE: lambda sc, c: sc.course_code in c.course_code,
    MatchMode.BOTH: lambda sc, c: sc.course_name == c.course_name
    and sc.course_code in c.course_code,
    MatchMode.EITHER: lambda sc, c: sc.course_name == c.course_name
    or sc.course_code in c.course_code,
}


class Configs:
    """
    Configuration options for course matching.
    """

    @staticmethod
    def dept(dept_code: str, mode: MatchMode = MatchMode.CODE) -> MatchConfig:
        return MatchConfig(mode, True, dept_code)

    @staticmethod
    def types(*course_types: int, mode: MatchMode = MatchMode.BOTH) -> MatchConfig:
        return MatchConfig(mode, course_types=frozenset(course_types))

    @staticmethod
    def categories(*categories: str, mode: MatchMode = MatchMode.BOTH) -> MatchConfig:
        return MatchConfig(mode, categories=frozenset(categories))

    @staticmethod
    def custom(
        mode: MatchMode = MatchMode.BOTH,
        dept_code: str = "",
        course_types: tuple[int, ...] = (),
        categories: tuple[str, ...] = (),
    ) -> MatchConfig:
        return MatchConfig(
            mode,
            bool(dept_code),
            dept_code,
            frozenset(course_types),
            frozenset(categories),
        )

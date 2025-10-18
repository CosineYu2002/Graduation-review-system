import pytest
from rule_engine.utils import UtilFunctions
from rule_engine.models.course import *
from rule_engine.models.rule import *
from rule_engine.models.result import *


class TestUtilFunctions:
    @pytest.mark.parametrize(
        "grade, expected_status",
        [
            (999, "修課中"),
            (555, "抵免"),
            (85, "及格"),
            (50, "不及格"),
            (150, "未知狀態"),
        ],
    )
    def test_get_status(self, grade, expected_status):
        assert UtilFunctions.get_status(grade) == expected_status

    def test_match_criteria_basic_pass(self):
        course = StudentCourse(
            course_name="計算機概論（一）",
            course_codes=["E216610"],
            credit=3.0,
            course_type=1,
            tag=[],
            grade=95,
            category=" ",
            year_taken=111,
            semester_taken=1,
            recognized=False,
        )

        criteria = CourseCriteria(department_codes=["E2"])

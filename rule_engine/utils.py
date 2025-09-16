from typing import Any
import re
from rule_engine.models.course import BaseCourse, StudentCourse, ResultCourse
from rule_engine.models.rule import *
from rule_engine.models.result import Result, SetResult, AllResult


class GradeUtils:
    @staticmethod
    def get_status(grade: int) -> str:
        if grade == 999:
            return "修課中"
        elif grade == 555:
            return "抵免"
        elif 60 <= grade <= 100:
            return "及格"
        elif 0 <= grade < 60:
            return "不及格"
        else:
            return "未知狀態"

    @staticmethod
    def match_criteria(
        course: StudentCourse,
        criteria: CourseCriteria,
    ) -> bool:
        """檢查學生課程是否符合篩選條件"""

        # 課程名稱模式
        if criteria.course_code_pattern:
            if not all(
                re.match(criteria.course_code_pattern, code)
                for code in course.course_codes
            ):
                return False

        # 課程代碼模式
        if criteria.course_name_pattern:
            if not re.match(criteria.course_name_pattern, course.course_name):
                return False

        # 系所條件
        if criteria.department_codes:
            if not any(
                code.startswith(dept)
                for code in course.course_codes
                for dept in criteria.department_codes
            ):
                return False
            else:
                if criteria.blacklist_courses:
                    if course.course_name in criteria.blacklist_courses:
                        return False

        if criteria.exclude_department_codes:
            if any(
                code.startswith(dept)
                for code in course.course_codes
                for dept in criteria.exclude_department_codes
            ):
                if criteria.whitelist_courses:
                    if course.course_name not in criteria.whitelist_courses:
                        return False
                else:
                    return False

        # 課程屬性
        if criteria.course_types:
            if course.course_type not in criteria.course_types:
                return False

        if criteria.categories:
            if course.category not in criteria.categories:
                return False

        if criteria.tags:
            if not all(tag in course.tag for tag in criteria.tags):
                return False

        if criteria.exclude_same_name:
            pass  # 這個條件需要在更高層次處理，因為需要知道本系課程名稱

        if criteria.series_courses:
            pass  # 這個條件需要在更高層次處理，因為需要知道系列課程的結構

        # 成績條件
        if not (60 <= course.grade <= 100) and not course.grade in (555, 999):
            if not criteria.allow_fail:
                return False
            else:
                if not (0 <= course.grade < 60):
                    return False

        return True

    @staticmethod
    def apply_requirement(
        rule: Rule,
        result: Result,
    ):
        """根據要求類型應用規則"""
        if isinstance(result, AllResult):
            total_credits = sum(course.credit for course in result.finished_course_list)
            total_courses = len(result.finished_course_list)
        else:
            total_credits = sum(
                sub_result.earned_credits for sub_result in result.sub_results
            )
            total_courses = 0  # make pylance happy

        match rule.requirement.type:
            case RequirementType.ALL:
                assert isinstance(rule, RuleAll)
                assert rule.course_list is not None
                result.is_valid = total_courses == len(rule.course_list)
                result.earned_credits = total_credits
            case RequirementType.MIN_CREDITS:
                result.is_valid = total_credits >= (rule.requirement.mincredits or 0)
                result.earned_credits = total_credits
            case RequirementType.MAX_CREDITS:
                result.is_valid = True
                if total_credits > (rule.requirement.maxcredits or float("inf")):
                    result.earned_credits = rule.requirement.maxcredits or 0
                else:
                    result.earned_credits = total_credits
            case RequirementType.MIN_COURSES:
                result.is_valid = total_courses >= (rule.requirement.mincourses or 0)
                result.earned_credits = total_credits
            case RequirementType.MAX_COURSES:
                result.is_valid = True
                if total_courses > (rule.requirement.maxcourses or float("inf")):
                    result.earned_credits = rule.requirement.maxcourses or 0
                else:
                    result.earned_credits = total_credits
            case RequirementType.PREREQUISITE:
                assert isinstance(rule, RuleAll)
                assert rule.course_list is not None
                result.is_valid = total_courses == len(rule.course_list)
                result.earned_credits = 0.0
            case RequirementType.CREDIT_RANGE:
                if (
                    rule.requirement.mincredits is not None
                    and rule.requirement.maxcredits is not None
                ):
                    result.is_valid = (
                        rule.requirement.mincredits
                        <= total_credits
                        <= rule.requirement.maxcredits
                    )
                    result.earned_credits = min(
                        max(total_credits, rule.requirement.mincredits),
                        rule.requirement.maxcredits,
                    )
                else:
                    raise ValueError(
                        "學分區間需求需要同時指定 mincredits 與 maxcredits"
                    )
            case _:
                raise ValueError(f"未知的需求類型: {requirement.type}")

from typing import Any
import re
from rule_engine.models.course import Course, StudentCourse, ResultCourse
from rule_engine.models.rule import CourseCriteria, RuleRequirement, RequirementType
from rule_engine.models.result import Result, SetResult, ListResult, CriteriaResult


class GradeUtils:
    @staticmethod
    def is_passing_grade(grade: int) -> bool:
        return 60 <= grade <= 100 or grade in (555, 999)

    @staticmethod
    def get_status(grade: int) -> str:
        if grade == 999:
            return "免修"
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
        course: Course,
        student_course: StudentCourse,
        criteria: CourseCriteria,
    ) -> bool:
        """檢查學生課程是否符合篩選條件"""

        # 課程名稱模式
        if criteria.course_code_pattern:
            if not re.match(criteria.course_code_pattern, student_course.course_code):
                return False

        # 課程代碼模式
        if criteria.course_name_pattern:
            if not re.match(criteria.course_name_pattern, student_course.course_name):
                return False

        # 系所條件
        if criteria.department_codes:
            if not any(
                student_course.course_code.startswith(code)
                for code in criteria.department_codes
            ):
                return False

        if criteria.exclude_department_codes:
            if any(
                student_course.course_code.startswith(dept)
                for dept in criteria.exclude_department_codes
            ):
                return False

        # 課程屬性
        if criteria.course_types:
            if student_course.course_type not in criteria.course_types:
                return False

        if criteria.categories:
            if student_course.category not in criteria.categories:
                return False

        if criteria.tags:
            if not any(tag in course.tag for tag in criteria.tags):
                return False

        # 白名單/黑名單
        if criteria.whitelist_courses:
            if student_course.course_name not in criteria.whitelist_courses:
                return False

        if criteria.blacklist_courses:
            if student_course.course_name in criteria.blacklist_courses:
                return False

        return True

    @staticmethod
    def apply_requirement(
        requirement: RuleRequirement,
        matched_courses: list[StudentCourse],
        result: Result,
    ) -> Result:
        """根據要求類型應用規則"""
        total_credits = sum(course.credit for course in matched_courses)
        total_courses = len(matched_courses)

        result.earned_credits = total_credits

        for course in matched_courses:
            result_course = ResultCourse(
                course_name=course.course_name,
                credit=course.credit,
                year_taken=course.year_taken,
                semester_taken=course.semester_taken,
                status="通過",
                grade=course.grade,
            )
            # result.course_list.append(result_course)

        match requirement.type:
            case RequirementType.ALL:
                result.is_valid = total_courses > 0
            case RequirementType.MIN_CREDITS:
                result.is_valid = total_credits >= (requirement.mincredits or 0)

            case RequirementType.MIN_COURSES:
                result.is_valid = total_courses >= (requirement.mincourses or 0)

        return result

    @staticmethod
    def course_match_by_name(student_course: StudentCourse, course: Course) -> bool:
        """檢查課程名稱是否符合"""
        return student_course.course_name == course.course_name

    @staticmethod
    def is_grade_acceptable(
        student_course: StudentCourse, requirement: RuleRequirement
    ) -> bool:
        """檢查成績是否可接受"""
        if requirement.allow_fail:
            return True  # 允許不及格
        return GradeUtils.is_passing_grade(student_course.grade)

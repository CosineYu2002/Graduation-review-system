from typing import Protocol
from abc import abstractmethod
from pydantic import TypeAdapter
from typing import Any
from rule_engine.models.course import BaseCourse, StudentCourse, ResultCourse
from rule_engine.models.graduation_rule import GraduationRule
from rule_engine.models.rule import *
from rule_engine.models.student import StudentType
from rule_engine.exception import *
from rule_engine.utils import GradeUtils
from rule_engine.models.result import *


class RuleEvaluator(Protocol):
    @abstractmethod
    def evaluate(
        self,
        rule: Rule,
        student_courses: list[StudentCourse],
        context: dict[str, Any] | None = None,
    ) -> Result: ...


class EvaluatorRegistry:
    def __init__(self):
        self._evaluators: dict[RuleTypeEnum, type[RuleEvaluator]] = {}

    def register(self, rule_type: RuleTypeEnum, evaluator: type[RuleEvaluator]):
        self._evaluators[rule_type] = evaluator

    def get_evaluator(self, rule_type: RuleTypeEnum) -> type[RuleEvaluator]:
        return self._evaluators[rule_type]

    def create_evaluator(self, rule_type: RuleTypeEnum) -> RuleEvaluator:
        evaluator_class = self.get_evaluator(rule_type)
        return evaluator_class()


evaluator_registry = EvaluatorRegistry()


def register_evaluator(rule_type: RuleTypeEnum):
    def decorator(cls):
        evaluator_registry.register(rule_type, cls)
        return cls

    return decorator


@register_evaluator(RuleTypeEnum.RULE_SET)
class RuleSetEvaluator:
    def evaluate(self, rule: RuleSet, student_courses: list[StudentCourse]) -> Result:
        adapter = TypeAdapter(Result)
        result = adapter.validate_python(
            {
                "result_type": RuleTypeEnum.RULE_SET,
                "name": rule.name,
                "description": rule.description,
                "sub_rule_logic": rule.sub_rule_logic,
            }
        )
        assert isinstance(result, SetResult)

        for sub_rule in rule.sub_rules:
            evaluator = evaluator_registry.create_evaluator(sub_rule.rule_type)
            sub_result = evaluator.evaluate(sub_rule, student_courses)
            result.sub_results.append(sub_result)

        if rule.sub_rule_logic == "AND":
            result.is_valid = all(sub.is_valid for sub in result.sub_results)
        else:
            result.is_valid = any(sub.is_valid for sub in result.sub_results)

        result.earned_credits = sum(sub.earned_credits for sub in result.sub_results)
        return result


@register_evaluator(RuleTypeEnum.RULE_LIST)
class RuleListEvaluator:
    def evaluate(self, rule: RuleList, student_courses: list[StudentCourse]) -> Result:
        adapter = TypeAdapter(Result)
        result = adapter.validate_python(
            {
                "result_type": RuleTypeEnum.RULE_LIST,
                "name": rule.name,
                "description": rule.description,
                "total_required_courses": rule.course_list,
            }
        )
        matched_courses: list[ResultCourse] = []

        for course in rule.course_list:
            matching_courses: list[StudentCourse] = []
            for student_course in student_courses:
                if not student_course.recognized:
                    if student_course.course_name == course.course_name:
                        matching_courses.append(student_course)

            if not matching_courses:
                matched_courses.append(
                    ResultCourse(
                        course_name=course.course_name,
                        course_codes=course.course_codes,
                        credit=course.credit,
                        course_type=course.course_type,
                        tag=course.tag,
                        status="未修課",
                        year_taken=0,
                        semester_taken=0,
                    )
                )
                continue

            for student_course in matching_courses:
                if GradeUtils.is_grade_acceptable(student_course, rule.requirement):
                    matched_courses.append(
                        ResultCourse(
                            year_taken=student_course.year_taken,
                            semester_taken=student_course.semester_taken,
                        )
                    )
                    student_course.recognized = True
                    break
        return GradeUtils.apply_requirement(rule.requirement, matched_courses, result)


@register_evaluator(RuleTypeEnum.RULE_CRITERIA)
class RuleCriteriaEvaluator:
    def evaluate(
        self, rule: RuleCriteria, student_courses: list[StudentCourse]
    ) -> Result:
        adapter = TypeAdapter(Result)
        result = adapter.validate_python(
            {
                "result_type": RuleTypeEnum.RULE_CRITERIA,
                "name": rule.name,
                "description": rule.description,
            }
        )
        matched_courses = []

        for student_course in student_courses:
            if not student_course.recognized:
                if GradeUtils.match_criteria(student_course, rule.course_criteria):
                    if GradeUtils.is_grade_acceptable(student_course, rule.requirement):
                        matched_courses.append(student_course)
                        student_course.recognized = True
        return GradeUtils.apply_requirement(rule.requirement, matched_courses, result)


class Evaluator:
    def __init__(self):
        self.registry = evaluator_registry

    def evaluate(
        self, graduation_rule: GraduationRule, student_courses: list[StudentCourse]
    ) -> list[Result]:
        results: list[Result] = []

        for rule in graduation_rule.rules:
            try:
                evaluator = self.registry.create_evaluator(rule.rule_type)
                result = evaluator.evaluate(rule, student_courses)
                results.append(result)
            except Exception as e:
                raise TypeError(f"未知的規則類型：{rule.rule_type}") from e
        return results


'''
class RuleEvaluator(Protocol):
    @abstractmethod
    def evaluate(
        self, rule: Rule, student_courses: list[StudentCourse], **kwargs
    ) -> EvaluationResult: ...


class EvaluatorRegistry:
    def __init__(self):
        self._evaluators: dict[str, type[RuleEvaluator]] = {}

    def register(self, rule_type: str, evaluator: type[RuleEvaluator]):
        self._evaluators[rule_type] = evaluator

    def get_evaluator(self, rule_type: str) -> type[RuleEvaluator]:
        if rule_type not in self._evaluators:
            raise ValueError(f"未註冊的規則類型: {rule_type}")
        return self._evaluators[rule_type]

    def create_evaluator(self, rule_type: str) -> RuleEvaluator:
        evaluator_class = self.get_evaluator(rule_type)
        return evaluator_class()


evaluator_registry = EvaluatorRegistry()


def register_evaluator(rule_type: str):
    def decorator(cls):
        evaluator_registry.register(rule_type, cls)
        return cls

    return decorator


@register_evaluator("list_selected")
class ListSelectedEvaluator:
    def evaluate(
        self, rule: ListSelectedRule, student_courses: list[StudentCourse], **kwargs
    ) -> EvaluationResult:
        result = EvaluationResult(course_list=[])
        course_count = 0
        for course in rule.course_list:
            for student_course in student_courses:
                if not student_course.recognized:
                    if CourseMatcher.match(
                        student_course,
                        course,
                        MatchConfig(),
                    ):
                        result.earned_credits += course.credit
                        course_count += 1
                        student_course.recognized = True
                        break
        if rule.min_credits is not None:
            if result.earned_credits >= rule.min_credits:
                result.is_valid = True
            else:
                result.is_valid = False
        if rule.min_course_number is not None:
            if course_count >= rule.min_course_number:
                result.is_valid = True
            else:
                result.is_valid = False
        return result


@register_evaluator("required")
class RequiredEvaluator:
    def evaluate(
        self, rule: RequiredRule, student_courses: list[StudentCourse], **kwargs
    ) -> EvaluationResult:
        result = EvaluationResult()
        department_code = kwargs.get("major", "")

        for course in rule.course_list:
            resultCourse = ResultCourse(
                course_name=course.course_name,
                credit=course.credit,
                semester=0,
                year=0,
                status="未修課",
                grade=0,
            )

            found = False

            # 第一階段：嚴格匹配本系課程
            for student_course in student_courses:
                if not student_course.recognized:
                    if CourseMatcher.match(
                        student_course,
                        course,
                        MatchConfig(
                            dept_code=department_code,
                        ),
                    ) and GradeUtils.is_passing_grade(student_course.grade):
                        result.earned_credits += course.credit
                        student_course.recognized = True
                        found = True
                        resultCourse.semester = student_course.semester
                        resultCourse.year = student_course.year
                        resultCourse.grade = student_course.grade
                        if student_course.grade == 999:
                            resultCourse.status = "修課中"
                        elif student_course.grade == 555:
                            resultCourse.status = "抵免"
                        else:
                            resultCourse.status = "通過"
                        break

            # 第二階段：外系同名課程
            if not found and rule.allow_external_substitute_after_fail:
                failed_dept_course = self._find_failed_department_course(
                    course, student_courses, department_code
                )
                if failed_dept_course:
                    external_course = self._find_external_substitute(
                        course, student_courses, failed_dept_course
                    )
                    if external_course:
                        result.earned_credits += external_course.credit
                        external_course.recognized = True
                        found = True
                        resultCourse.semester = external_course.semester
                        resultCourse.year = external_course.year
                        resultCourse.grade = external_course.grade
                        resultCourse.status = "外系替代"
            if not found:
                result.is_valid = False

            result.course_list.append(resultCourse)

        return result

    def _find_failed_department_course(
        self, course: Course, student_courses: list[StudentCourse], dept_code: str
    ) -> StudentCourse | None:
        """尋找本系失敗的課程"""
        for student_course in student_courses:
            # 嚴格匹配本系課程且成績未通過
            if CourseMatcher.match(
                student_course,
                course,
                MatchConfig(dept_code=dept_code),
            ) and not GradeUtils.is_passing_grade(student_course.grade):
                return student_course
        return None

    def _find_external_substitute(
        self,
        course: Course,
        student_courses: list[StudentCourse],
        failed_course: StudentCourse,
    ) -> StudentCourse | None:
        """尋找外系同名替代課程"""
        for student_course in student_courses:
            if student_course.recognized:
                continue

            # 同名但非本系課程（使用 NAME_ONLY 模式）
            if (
                CourseMatcher.match(
                    student_course,
                    course,
                    MatchConfig(
                        mode=MatchMode.NAME,
                        learn_in_dept=False,
                    ),
                )
                and student_course.course_code not in course.course_codes
                and GradeUtils.is_passing_grade(student_course.grade)
            ):

                # 檢查時間順序：必須晚於被當的本系課程
                if self._is_later_than(student_course, failed_course):
                    return student_course

        return None

    def _is_later_than(
        self, later_course: StudentCourse, earlier_course: StudentCourse
    ) -> bool:
        """檢查課程時間順序"""
        # 年度不同：後面的年度較大
        if later_course.year != earlier_course.year:
            return later_course.year > earlier_course.year

        # 同年度：學期較大
        return later_course.semester > earlier_course.semester


@register_evaluator("selected")
class SelectedEvaluator:
    def evaluate(
        self, rule: SelectedRule, student_courses: list[StudentCourse], **kwargs
    ) -> EvaluationResult:
        result = EvaluationResult()
        return result


@register_evaluator("prerequisite")
class PrerequisiteEvaluator:
    def evaluate(
        self, rule: PrerequisiteRule, student_courses: list[StudentCourse]
    ) -> EvaluationResult:
        result = EvaluationResult(course_list=[])
        for course in rule.course_list:
            for student_course in student_courses:
                if not student_course.recognized:
                    if CourseMatcher.match(student_course, course, MatchConfig()):
                        student_course.recognized = True
                        break
            result.is_valid = False
            break
        return result


@register_evaluator("corresponding")
class CorrespondingEvaluator:
    def evaluate(
        self, rule: CorrespondingRule, student_courses: list[StudentCourse]
    ) -> EvaluationResult:
        result = EvaluationResult(course_list=[])
        for course in rule.course_list:
            for student_course in student_courses:
                if not student_course.recognized:
                    if CourseMatcher.match(student_course, course, MatchConfig()):
                        student_course.recognized = True
                        result.earned_credits += course.credit
                        break
        return result


@register_evaluator("any_selected")
class AnySelectedEvaluator:
    def evaluate(
        self,
        rule: AnySelectedRule,
        student_courses: list[StudentCourse],
    ) -> EvaluationResult:
        result = EvaluationResult(course_list=[])
        course_count = 0
        if rule.learn_in_dept:
            for student_course in student_courses:
                department_code = "12"
                if (
                    student_course.course_code[0:2] == department_code
                    and student_course.course_type == 2
                ):
                    student_course.recognized = True
                    result.earned_credits += student_course.credit
                    course_count += 1
        else:
            for student_course in student_courses:
                if student_course.course_type == 2:
                    student_course.recognized = True
                    result.earned_credits += student_course.credit
                    course_count += 1
        if rule.min_credits is not None:
            if result.earned_credits < rule.min_credits:
                result.is_valid = False
        if rule.min_course_number is not None:
            if course_count < rule.min_course_number:
                result.is_valid = False
        return result


@register_evaluator("ccep_pro_field")
class CCEPProFieldEvaluator:
    def evaluate(
        self, rule: CCEPProFieldRule, student_courses: list[StudentCourse]
    ) -> EvaluationResult:
        result = EvaluationResult(course_list=[])
        return result


@register_evaluator("final")
class FinalEvaluator:
    def evaluate(
        self, rule: FinalRule, results: list[EvaluationResult]
    ) -> EvaluationResult:
        result = EvaluationResult(course_list=[])
        for res in results:
            result.earned_credits += res.earned_credits
        if result.earned_credits < rule.min_credits:
            result.is_valid = False
        return result


class Evaluator:
    def __init__(self):
        self.registry = evaluator_registry

    def evaluate(
        self, graduation_rule: GraduationRule, student_courses: list[StudentCourse]
    ) -> list[EvaluationResult]:
        results: list[EvaluationResult] = []
        for rule in graduation_rule.rules:
            try:
                evaluator = self.registry.create_evaluator(rule.rule_type)
                result = evaluator.evaluate(rule, student_courses)
                results.append(result)
            except ValueError as e:
                raise TypeError(f"未知的規則類型：{rule.rule_type}") from e
        return results
'''

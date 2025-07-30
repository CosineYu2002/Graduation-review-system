from dataclasses import dataclass, field
from rule_engine.models.course import Course, StudentCourse
from rule_engine.models.rule import *
from rule_engine.course_matcher import CourseMathcer
from rule_engine.models.graduation_rule import GraduationRule


@dataclass
class EvaluationResult:
    is_valid: bool = True
    earned_credits: float = 0.0


class Evaluator:
    def __init__(self):
        self.results = EvaluationResult()

    def evaluate(
        self, graduation_rule: GraduationRule, student_courses: list[StudentCourse]
    ) -> bool:
        for rule in graduation_rule.rules:
            self.evaluate_rule(rule, student_courses, graduation_rule.department_code)
        return self.results.is_valid

    def evaluate_rule(
        self, rule: BaseRule, student_courses: list[StudentCourse], department_code: str
    ):
        if isinstance(rule, ListSelectedRule):
            return self._evaluate_list_selected(rule, student_courses)
        elif isinstance(rule, RequiredRule):
            return self._evaluate_required(rule, student_courses)
        elif isinstance(rule, PrerequisiteRule):
            return self._evaluate_prerequisite(rule, student_courses)
        elif isinstance(rule, CorrespondingRule):
            return self._evaluate_corresponding(rule, student_courses)
        elif isinstance(rule, AnySelectedRule):
            return self._evaluate_any_selected(rule, student_courses, department_code)
        elif isinstance(rule, FinalRule):
            return self._evaluate_final(rule, student_courses)
        else:
            raise TypeError(f"未知的規則類型: {type(rule)}")

    def _evaluate_list_selected(
        self, rule: ListSelectedRule, student_courses: list[StudentCourse]
    ):
        credits = 0.0
        course_count = 0
        for course in rule.course_list:
            for student_course in student_courses:
                if not student_course.recognized:
                    if CourseMathcer.is_match(
                        student_course, course, rule.learn_in_dept
                    ):
                        credits += course.credits
                        course_count += 1
                        student_course.recognized = True
                        break
        self.results.earned_credits += credits
        if rule.min_credits is not None:
            if credits >= rule.min_credits:
                self.results.is_valid &= True
            else:
                self.results.is_valid &= False
        if rule.min_course_number is not None:
            if course_count >= rule.min_course_number:
                self.results.is_valid &= True
            else:
                self.results.is_valid &= False

    def _evaluate_required(
        self, rule: RequiredRule, student_courses: list[StudentCourse]
    ):
        credits = 0.0
        for course in rule.course_list:
            find = False
            for student_course in student_courses:
                if not student_course.recognized:
                    if CourseMathcer.is_match(
                        student_course, course, rule.learn_in_dept
                    ):
                        credits += course.credits
                        student_course.recognized = True
                        find = True
                        break
            if not find:
                self.results.is_valid &= False
        self.results.earned_credits += credits

    def _evaluate_prerequisite(
        self, rule: PrerequisiteRule, student_courses: list[StudentCourse]
    ):
        for course in rule.course_list:
            for student_course in student_courses:
                if not student_course.recognized:
                    if CourseMathcer.is_match(
                        student_course, course, rule.learn_in_dept
                    ):
                        student_course.recognized = True
                        break
            self.results.is_valid &= False
            break

    def _evaluate_corresponding(
        self, rule: CorrespondingRule, student_courses: list[StudentCourse]
    ):
        credits = 0.0
        for course in rule.course_list:
            for student_course in student_courses:
                if not student_course.recognized:
                    if CourseMathcer.is_match(
                        student_course, course, rule.learn_in_dept
                    ):
                        student_course.recognized = True
                        credits += course.credits
                        break

    def _evaluate_any_selected(
        self,
        rule: AnySelectedRule,
        student_courses: list[StudentCourse],
        department_code: str,
    ):
        credits = 0.0
        course_count = 0
        if rule.learn_in_dept:
            for student_course in student_courses:
                if (
                    student_course.course_code[0:2] == department_code
                    and student_course.course_type == 2
                ):
                    student_course.recognized = True
                    credits += student_course.credits
                    course_count += 1
        else:
            for student_course in student_courses:
                if student_course.course_type == 2:
                    student_course.recognized = True
                    credits += student_course.credits
                    course_count += 1
        self.results.earned_credits += credits
        if rule.min_credits is not None:
            if credits < rule.min_credits:
                self.results.is_valid &= False
        if rule.min_course_number is not None:
            if course_count < rule.min_course_number:
                self.results.is_valid &= False

    def _evaluate_final(self, rule: FinalRule, student_courses: list[StudentCourse]):
        if self.results.earned_credits < rule.min_credits:
            self.results.is_valid = False

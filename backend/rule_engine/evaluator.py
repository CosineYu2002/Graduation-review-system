from typing import Protocol
from abc import abstractmethod
from pydantic import TypeAdapter
from rule_engine.models.course import StudentCourse, ResultCourse
from rule_engine.models.rule import *
from rule_engine.exception import *
from rule_engine.utils import UtilFunctions
from rule_engine.models.result import *


class RuleEvaluator(Protocol):
    @abstractmethod
    def evaluate(
        self,
        rule: Rule,
        student_courses: list[StudentCourse],
    ) -> Result: ...


class EvaluatorRegistry:
    def __init__(self):
        self._evaluators: dict[str, type[RuleEvaluator]] = {}

    def register(self, rule_type: str, evaluator: type[RuleEvaluator]):
        self._evaluators[rule_type] = evaluator

    def get_evaluator(self, rule_type: str) -> type[RuleEvaluator]:
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


@register_evaluator("rule_set")
class RuleSetEvaluator:
    def evaluate(self, rule: RuleSet, student_courses: list[StudentCourse]) -> Result:
        adapter = TypeAdapter(Result)
        result = adapter.validate_python(
            {
                "result_type": "rule_set",
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


@register_evaluator("rule_all")
class RuleAllEvaluator:
    def evaluate(self, rule: RuleAll, student_courses: list[StudentCourse]) -> Result:
        adapter = TypeAdapter(Result)
        result = adapter.validate_python(
            {
                "result_type": "rule_all",
                "name": rule.name,
                "description": rule.description,
                "required_course_list": rule.course_list,
            }
        )
        assert isinstance(result, AllResult)
        matched_courses: list[ResultCourse] = []
        matching_courses: list[StudentCourse] = []

        if rule.course_list is None:
            matching_courses = [sc for sc in student_courses if not sc.recognized]
        else:
            result.required_course_list = rule.course_list
            for course in rule.course_list:
                for student_course in student_courses:
                    if not student_course.recognized:
                        if student_course.course_name == course:
                            matching_courses.append(student_course)

        sorted_matching_courses = sorted(
            matching_courses,
            key=lambda c: (c.course_name, c.year_taken, c.semester_taken, c.grade),
        )

        if sorted_matching_courses:
            i = 0
            while i < len(sorted_matching_courses):
                current_course = sorted_matching_courses[i]
                if UtilFunctions.match_criteria(current_course, rule.course_criteria):
                    matched_courses.append(
                        ResultCourse(
                            course_name=current_course.course_name,
                            course_codes=current_course.course_codes,
                            credit=current_course.credit,
                            course_type=current_course.course_type,
                            tag=current_course.tag,
                            year_taken=current_course.year_taken,
                            semester_taken=current_course.semester_taken,
                            status=UtilFunctions.get_status(current_course.grade),
                        )
                    )
                    current_course.recognized = True
                    result.earned_credits += current_course.credit
                    i += 1
                elif (
                    rule.course_criteria.allow_external_substitute_after_fail
                    and current_course.grade < 60
                ):
                    same_name_courses = []
                    j = i + 1
                    while (
                        j < len(sorted_matching_courses)
                        and sorted_matching_courses[j].course_name
                        == current_course.course_name
                    ):
                        same_name_courses.append(sorted_matching_courses[j])
                        j += 1
                    best_passing_course = None
                    for course in same_name_courses:
                        if course.grade >= 60:
                            if (
                                best_passing_course is None
                                or course.grade > best_passing_course.grade
                            ):
                                best_passing_course = course

                    if best_passing_course:
                        temp_course = current_course.model_copy(update={"grade": 60})
                        if UtilFunctions.match_criteria(
                            temp_course, rule.course_criteria
                        ):
                            matched_courses.append(
                                ResultCourse(
                                    course_name=current_course.course_name,
                                    course_codes=current_course.course_codes,
                                    credit=current_course.credit,
                                    course_type=current_course.course_type,
                                    tag=current_course.tag,
                                    year_taken=current_course.year_taken,
                                    semester_taken=current_course.semester_taken,
                                    status="外系承抵",
                                )
                            )
                            for course in same_name_courses:
                                course.recognized = True
                            result.earned_credits += current_course.credit
                            i = j
                else:
                    i += 1
            result.finished_course_list = matched_courses
        UtilFunctions.apply_requirement(rule, result)
        return result


class Evaluator:
    def __init__(self):
        self.registry = evaluator_registry

    def evaluate(self, rule: Rule, student_courses: list[StudentCourse]) -> Result:
        for course in student_courses:
            course.recognized = False

        try:
            evaluator = self.registry.create_evaluator(rule.rule_type)
            result = evaluator.evaluate(rule, student_courses)
        except Exception as e:
            raise TypeError(f"未知的規則類型：{rule.rule_type}") from e
        return result

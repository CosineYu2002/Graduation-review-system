from rule_engine.exceptions import InvalidRuleDataError
from rule_engine.loader import load_course
import os


def evaluator_rule(rule, student):
    """
    Evaluate the rule against the student data.
    Args:
        rule (dict): The rule to evaluate.
        student (dict): The student data to evaluate against.
    Returns:
        bool: True if the rule is satisfied, False otherwise.
    """
    student_id = student.get("id")
    if student_id[5] == "9":
        admission_year = int(student_id[3:5]) + 99
    else:
        admission_year = int(student_id[3:5]) + 100

    applied_rule = None
    for rule_year, rule_value in rule.items():
        if admission_year >= int(rule_year):
            applied_rule = rule_value
        else:
            break

    if not applied_rule:
        raise InvalidRuleDataError(
            f"The rule of {next(iter(rule.values()))[-1]["department_name"]} does not apply to student {student_id} because there is no corresponding rule for his/her admission year."
        )

    for rule_item in applied_rule:
        match rule_item["type"]:
            case "list_selected":
                student_courses_set = {
                    course["course_code"]
                    for course in student["courses"]
                    if not (
                        course["category"] in {"J", "R", "T", "X", "Y"}
                        and course["grade"] in {111, 777}
                    )
                    and course["grade"] >= 60
                }
                missing_courses = []
                selected_courses = load_course(
                    os.path.join("data", rule_item["target"])
                )
                for course_name, (credit, course_code_list) in selected_courses.items():
                    if isinstance(course_code_list, str):
                        course_code_list = [course_code_list]

                    if not any(
                        course_code in student_courses_set
                        for course_code in course_code_list
                    ):
                        missing_courses.append(course_name)

                if missing_courses:
                    print(f"missing courses: {missing_courses}")
                else:
                    print("All selected courses are completed.")
            case "required":
                print("2")
            case "final":
                print("3")

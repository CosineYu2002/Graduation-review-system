import json
import os


def load_rule(rule_file_path):
    """
    Load rule from a JSON file.
    Args:
        rule_file_path (str): Path to the JSON file containing rule.
    Returns:
        dictionary: A dictionary of rule loaded from the file.
    Raises:
        FileNotFoundError: If the rule file does not exist.
        json.JSONDecodeError: If the JSON file is not properly formatted.
        ValueError: If the rule does not contain required fields.
    """
    if not os.path.exists(rule_file_path):
        raise FileNotFoundError(f"Rules file not found: {rule_file_path}")

    with open(rule_file_path, "r", encoding="utf-8") as file:
        rule = json.load(file)
        if validate_rule(rule):
            return rule


def validate_rule(rule):
    """
    Validate the rule structure.
    Args:
        rule (dict): The rule to validate.
    Returns:
        bool: True if the rule is valid, False otherwise.
    Raises:
        ValueError: If the rule does not contain required fields.
    """
    allowed_keys = [
        "type",
        "target",
        "min_credits",
        "learn_in_department",
        "fallback_department",
        "total_credits",
        "department_name",
    ]
    for key, value in rule.items():
        if key.isdigit() and isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    for sub_key in item.keys():
                        if not sub_key in allowed_keys:
                            raise ValueError(f"Invalid rule structure: {sub_key}")
                else:
                    raise ValueError(f"Invalid rule structure: {item}")
        else:
            raise ValueError(f"Invalid rule structure: {key}")

    return True


def load_student(student_file_path):
    """
    Load student data from a JSON file.
    Args:
        student_file_path (str): Path to the JSON file containing student information.
    Returns:
        dictionary: A dictionary of student data loaded from the file.
    Raises:
        FileNotFoundError: If the student file does not exist.
        json.JSONDecodeError: If the JSON file is not properly formatted.
        ValueError: If the student data does not contain required fields.
    """
    if not os.path.exists(student_file_path):
        raise FileNotFoundError(f"Student file not found: {student_file_path}")

    with open(student_file_path, "r", encoding="utf-8") as file:
        student = json.load(file)

    for key, value in student.items():
        if key in ["id", "name"]:
            continue
        elif key == "courses":
            for course in value:
                if not isinstance(course, dict):
                    raise ValueError(f"Invalid student structure: {course}")
                for sub_key in course.keys():
                    if sub_key not in [
                        "course_name",
                        "course_code",
                        "credit",
                        "grade",
                        "category",
                    ]:
                        raise ValueError(f"Invalid student structure: {sub_key}")
        else:
            raise ValueError(f"Invalid student structure: {key}")

    return student


def load_course(course_file_path):
    """
    Load course data from a JSON file.
    Args:
        course_file_path (str): Path to the JSON file containing course information.
    Returns:
        dictionary: A dictionary of course data loaded from the file.
    Raises:
        FileNotFoundError: If the course file does not exist.
        json.JSONDecodeError: If the JSON file is not properly formatted.
    """
    if not os.path.exists(course_file_path):
        raise FileNotFoundError(f"Course file not found: {course_file_path}")

    with open(course_file_path, "r", encoding="utf-8") as file:
        course = json.load(file)

    return course

from .models.course import Course, StudentCourse


class CourseMathcer:
    @staticmethod
    def is_match(
        student_course: StudentCourse, course: Course, learn_in_depart: bool
    ) -> bool:
        """
        需要判斷的東西：
        1. 成績大於60小於等於100
        2. 其他成績需要額外甄別
        3. 是否在學系內
        4. 是否為認可的課程
        """
        if not isinstance(student_course, StudentCourse):
            raise TypeError("Invalid student_course type")
        if not isinstance(course, Course):
            raise TypeError("Invalid course type")
        grade = student_course.grade
        passed = 60 <= grade <= 100 or grade == 555 or grade == 999
        if not passed:
            return False
        if learn_in_depart:
            return student_course.course_code in course.course_codes
        else:
            return student_course.course_name == course.course_name

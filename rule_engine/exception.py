class GraduationReviewSystemError(Exception):
    def __init__(self, message: str, context: dict | None = None):
        super().__init__(message)
        self.context = context if context is not None else {}


class ModelError(GraduationReviewSystemError):
    pass


class DataValidationError(ModelError):
    pass


class MissingFieldError(DataValidationError):
    def __init__(self, field_name: str, data_type: str):
        super().__init__(
            f"{data_type}缺少必要的欄位: {field_name}",
            context={"field_name": field_name, "data_type": data_type},
        )


class InvalidTypeError(DataValidationError):
    def __init__(self, field_name: str, expected_type: type, actual_type: type):
        super().__init__(
            f"欄位 {field_name} 的資料類型不正確，預期 {expected_type.__name__}，實際 {actual_type.__name__}",
            context={
                "field_name": field_name,
                "expected_type": expected_type,
                "actual_type": actual_type,
            },
        )


class InvalidValueError(DataValidationError):
    def __init__(self, field_name: str, actual_value, reason: str):
        super().__init__(
            f"欄位 {field_name} 的值不正確，實際值: {actual_value}, 原因: {reason}",
            context={
                "field_name": field_name,
                "actual_value": str(actual_value),
                "reason": reason,
            },
        )

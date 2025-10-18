class GraduationReviewSystemError(Exception):
    def __init__(self, message: str, context: dict | None = None):
        super().__init__(message)
        self.context = context if context is not None else {}


class ModelError(GraduationReviewSystemError):
    pass


class DataValidationError(ModelError):
    def __init__(self, message: str, errors: list | None = None):
        super().__init__(message)
        self.errors = errors if errors is not None else []

class InvalidRuleDataError(Exception):
    """Exception raised for invalid rule data."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

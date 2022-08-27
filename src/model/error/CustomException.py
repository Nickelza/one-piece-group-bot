class PredictionException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class OpponentValidationException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)

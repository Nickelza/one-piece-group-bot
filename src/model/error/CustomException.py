class PredictionException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class OpponentValidationException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class GroupMessageValidationException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class CrewValidationException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class CommandValidationException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class CrewJoinValidationCrewException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class CrewJoinValidationUserException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)

class PredictionException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class OpponentValidationException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class GroupMessageValidationException(Exception):
    def __init__(self, message=None, notification: any = None):
        self.message = message
        self.notification = notification
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


class NavigationLimitReachedException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class DevilFruitValidationException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class DevilFruitTradeValidationException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class WikiException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class BountyLoanValidationException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class StepValidationException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class DateValidationException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class UnauthorizedToViewItemException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class BellyValidationException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class AnonymousAdminException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class ImpelDownValidationException(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)

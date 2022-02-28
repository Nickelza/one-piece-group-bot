from src.model.error.ErrorSource import ErrorSource


class Error:
    """
    Error class
    """

    def __init__(self, code, message, source: ErrorSource, need_admin=False):
        self.code = code
        self.message = message
        self.source = source
        self.need_admin = need_admin

    def __str__(self):
        result = 'Error ' + self.source.value + str(self.code) + ': ' + self.message
        if self.need_admin:
            result += '. Please forward this message to an Admin.'
        return result

    def build(self):
        return str(self)

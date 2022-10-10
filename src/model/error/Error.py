from src.model.error.ErrorSource import ErrorSource


class Error:
    """
    Error class
    """

    def __init__(self, code, message, source: ErrorSource):
        self.code = code
        self.message = message
        self.source = source

    def __str__(self):
        result = f'Error ' + self.source + str(self.code) + ': ' + self.message
        result += '. Please forward this message to an Admin.'

        return result

    def build(self):
        return str(self)

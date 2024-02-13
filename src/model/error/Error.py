from src.model.error.ErrorSource import ErrorSource


class Error:
    """
    Error class
    """

    def __init__(self, code, message, source: ErrorSource, only_message: bool = False):
        self.code = code
        self.message = message
        self.source = source
        self.only_message = only_message

    def __str__(self):
        if self.only_message:
            return self.message

        result = f"Error " + self.source + str(self.code) + ": " + self.message
        result += ". Please forward this message to an Admin."

        return result

    def build(self):
        return str(self)

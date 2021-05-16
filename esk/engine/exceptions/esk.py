class ESKException(Exception):
    def __init__(self, status_code, message):
        self.status = status_code
        self.message = message

    def __str__(self) -> str:
        return f"{ self.status }: { self.message }"


class ValueUnrecoverable(ESKException):
    def __init__(self, message):
        self.__message = message

    def __str__(self) -> str:
        return f"409: { self.__message }"

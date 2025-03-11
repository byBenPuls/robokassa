class RobokassaException(Exception):
    pass


class UnresolvedAlgorithmTypeError(RobokassaException):
    pass


class UnusedStrictUrlParameterError(RobokassaException):
    pass


class UnusedParameterError(RobokassaException):
    pass


class IncorrectUrlMethodError(RobokassaException):
    pass


class RobokassaInterfaceError(RobokassaException):
    pass


class RobokassaParsingError(RobokassaException):
    pass


class RobokassaRequestError(RobokassaException):
    pass

class ServiceException(Exception):
    pass


class ServiceConflict(ServiceException):
    pass


class ServiceForbidden(ServiceException):
    pass


class ServiceUnauthorized(ServiceException):
    pass


class ServiceNotFound(ServiceException):
    pass


class ServiceLimitExceeded(ServiceException):
    pass

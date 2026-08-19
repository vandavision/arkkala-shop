class DomainException(Exception):
    """
    Base exception for all domain-related errors.
    """
    pass

class RateLimitExceededException(DomainException):
    """
    Raised when an entity exceeds operational limits.
    """
    pass

class WaitTimeException(DomainException):
    """
    Raised when an action is triggered before the required cooling period.
    """
    pass

class ValidationException(DomainException):
    """
    Raised when domain validation rules fail.
    """
    pass

class ResourceNotFoundException(DomainException):
    """
    Raised when a requested domain entity is missing.
    """
    pass
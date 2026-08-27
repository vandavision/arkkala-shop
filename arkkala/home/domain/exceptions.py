class HomeDomainException(Exception):
    """
    Base exception for the Home domain.
    """
    pass

class SingletonConstraintException(HomeDomainException):
    """
    Exception raised when attempting to create multiple instances of a Singleton entity.
    """
    pass
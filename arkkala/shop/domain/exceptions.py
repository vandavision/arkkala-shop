class DomainException(Exception):
    """Base Domain Exception."""
    pass

class ProductNotFoundError(DomainException):
    """Raised when a product is not found in the repository."""
    pass

class InvalidInteractionDataError(DomainException):
    """Raised when comment or question data violates business rules."""
    pass

class InvalidProductDataError(DomainException):
    """Raised when product creation payload violates core business constraints."""
    pass
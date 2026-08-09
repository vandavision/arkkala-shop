class OrderDomainException(Exception):
    """Base exception for order domain."""
    pass


class CartEmptyException(OrderDomainException):
    """Raised when attempting to checkout an empty cart."""
    pass


class InvalidCouponException(OrderDomainException):
    """Raised when a coupon is expired, inactive, or exhausted."""
    pass


class InvalidOrderActionException(OrderDomainException):
    """Raised when an order action (cancel/return) is not allowed based on current status."""
    pass
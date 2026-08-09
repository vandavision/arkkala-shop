class PaymentDomainException(Exception):
    """Base exception for payment domain."""
    pass

class PaymentGatewayException(PaymentDomainException):
    """Raised when external gateway rejects the request or verification."""
    pass

class InvalidPaymentOrderException(PaymentDomainException):
    """Raised when trying to pay for an order that is not pending."""
    pass
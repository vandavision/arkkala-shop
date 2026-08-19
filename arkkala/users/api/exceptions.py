from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from users.domain.exceptions import DomainException, ValidationException, RateLimitExceededException, WaitTimeException

def custom_exception_handler(exc, context):
    """
    Translates domain level deviations mapping appropriately formatted REST structures correctly.
    """
    response = exception_handler(exc, context)

    if isinstance(exc, RateLimitExceededException):
        return Response({"error": str(exc)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
    if isinstance(exc, WaitTimeException):
        return Response({"error": str(exc)}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    if isinstance(exc, ValidationException):
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    if isinstance(exc, DomainException):
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    return response
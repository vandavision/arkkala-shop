from functools import wraps
from typing import Any, Callable
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from shop.domain.exceptions import DomainException, ProductNotFoundError, InvalidInteractionDataError

def exception_handler_wrapper(view_func: Callable) -> Callable:
    """Decorator to map domain and validation exceptions to HTTP responses safely."""
    
    @wraps(view_func)
    def wrapped_view(*args: Any, **kwargs: Any) -> Response:
        try:
            return view_func(*args, **kwargs)
        except ProductNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except (InvalidInteractionDataError, ValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DomainException as e:
            return Response({"error": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    return wrapped_view
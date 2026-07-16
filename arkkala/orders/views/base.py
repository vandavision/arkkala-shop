from typing import Tuple, Optional
from django.contrib.auth.models import AbstractUser
from rest_framework.request import Request


class CustomerIdentifiedMixin:
    """Base Mixin providing reusable identity extraction for Cart/Orders."""
    
    def get_identity(self, request: Request) -> Tuple[Optional[AbstractUser], Optional[str]]:
        """Returns (user, guest_id) cleanly."""
        user = request.user if request.user and request.user.is_authenticated else None
        guest_id = request.headers.get('X-Guest-ID')
        return user, guest_id
from typing import Optional, Any
from django.utils import timezone
from users.models.otp import OTPRequest
from users.application.ports.repositories import OTPRepositoryPort

class OTPRepositoryImpl(OTPRepositoryPort):
    """
    Concrete implementation securing transient request lifecycles directly internally.
    """
    def get_valid_otp(self, identifier: str, code: str) -> Optional[Any]:
        return OTPRequest.objects.filter(
            identifier=identifier,
            code=code,
            is_used=False,
            expires_at__gte=timezone.now()
        ).first()

    def count_requests_since(self, identifier: str, since: Any) -> int:
        return OTPRequest.objects.filter(
            identifier=identifier,
            created_at__gte=since
        ).count()

    def get_latest_request(self, identifier: str) -> Optional[Any]:
        return OTPRequest.objects.filter(identifier=identifier).order_by('-created_at').first()

    def save_request(self, request: Any) -> None:
        request.full_clean()
        request.save()

    def mark_as_used(self, request: Any) -> None:
        request.is_used = True
        request.save(update_fields=['is_used'])

    def delete_request(self, request: Any) -> None:
        request.delete()

    def delete_by_uuid(self, uuid: Any) -> None:
        OTPRequest.objects.filter(uuid=uuid).delete()
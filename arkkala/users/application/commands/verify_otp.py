from users.application.dto.commands import OTPVerifyDTO
from users.application.dto.responses import TokenResponseDTO
from users.application.ports.repositories import OTPRepositoryPort, UserRepositoryPort
from users.domain.exceptions import ValidationException
from users.domain.events import DomainEventPublisher
from rest_framework_simplejwt.tokens import RefreshToken

class VerifyOTPCommand:
    def __init__(self, otp_repo: OTPRepositoryPort, user_repo: UserRepositoryPort) -> None:
        self.otp_repo = otp_repo
        self.user_repo = user_repo

    def execute(self, dto: OTPVerifyDTO) -> TokenResponseDTO:
        otp_request = self.otp_repo.get_valid_otp(dto.identifier, dto.code)
        if not otp_request:
            raise ValidationException("کد وارد شده نامعتبر یا منقضی شده است.")

        self.otp_repo.mark_as_used(otp_request)
        user, created = self.user_repo.get_or_create_by_phone(dto.identifier)
        self.otp_repo.delete_request(otp_request)

        if created:
            DomainEventPublisher.publish("UserRegisteredViaOTP", {"user_id": str(user.id)})
        DomainEventPublisher.publish("UserLoggedIn", {"user_id": str(user.id)})

        refresh = RefreshToken.for_user(user)
        return TokenResponseDTO(
            access_token=str(refresh.access_token),
            refresh_token=str(refresh),
            is_new_user=created
        )
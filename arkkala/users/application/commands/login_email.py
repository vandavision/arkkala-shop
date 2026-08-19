from users.application.dto.commands import EmailLoginDTO
from users.application.dto.responses import TokenResponseDTO
from users.application.ports.repositories import UserRepositoryPort
from users.domain.exceptions import ValidationException
from users.domain.events import DomainEventPublisher
from rest_framework_simplejwt.tokens import RefreshToken

class LoginEmailCommand:
    def __init__(self, user_repo: UserRepositoryPort) -> None:
        self.user_repo = user_repo

    def execute(self, dto: EmailLoginDTO) -> TokenResponseDTO:
        user = self.user_repo.get_by_email(dto.email)
        if not user or not user.check_password(dto.password):
            raise ValidationException("ایمیل یا رمز عبور اشتباه است.")

        DomainEventPublisher.publish("UserLoggedIn", {"user_id": str(user.id)})

        refresh = RefreshToken.for_user(user)
        return TokenResponseDTO(
            access_token=str(refresh.access_token),
            refresh_token=str(refresh),
            is_new_user=False
        )
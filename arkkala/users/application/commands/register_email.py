from users.application.dto.commands import EmailRegisterDTO
from users.application.ports.repositories import UserRepositoryPort
from users.domain.exceptions import ValidationException
from users.domain.events import DomainEventPublisher
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterEmailCommand:
    def __init__(self, user_repo: UserRepositoryPort) -> None:
        self.user_repo = user_repo

    def execute(self, dto: EmailRegisterDTO) -> None:
        if self.user_repo.get_by_email(dto.email):
            raise ValidationException("این ایمیل قبلاً ثبت شده است.")

        user = User(username=dto.email, email=dto.email)
        user.set_password(dto.password)
        self.user_repo.save_user(user)

        DomainEventPublisher.publish("UserRegisteredViaEmail", {"user_id": str(user.id)})
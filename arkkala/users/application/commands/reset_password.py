from users.application.dto.commands import PasswordResetConfirmDTO
from users.application.ports.repositories import OTPRepositoryPort, UserRepositoryPort
from users.domain.exceptions import ValidationException
from users.domain.events import DomainEventPublisher

class ResetPasswordCommand:
    def __init__(self, otp_repo: OTPRepositoryPort, user_repo: UserRepositoryPort) -> None:
        self.otp_repo = otp_repo
        self.user_repo = user_repo

    def execute(self, dto: PasswordResetConfirmDTO) -> None:
        otp_request = self.otp_repo.get_valid_otp(dto.email, dto.code)
        if not otp_request:
            raise ValidationException("کد تایید نامعتبر یا منقضی شده است.")

        user = self.user_repo.get_by_email(dto.email)
        if not user:
            raise ValidationException("کاربری با این ایمیل یافت نشد.")

        user.set_password(dto.new_password)
        self.user_repo.save_user(user)
        self.otp_repo.delete_request(otp_request)
        
        DomainEventPublisher.publish("UserPasswordReset", {"user_id": str(user.id)})
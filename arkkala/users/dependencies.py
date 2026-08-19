from django.conf import settings
from users.infrastructure.repositories.user import UserRepositoryImpl
from users.infrastructure.repositories.otp import OTPRepositoryImpl
from users.infrastructure.repositories.address import AddressRepositoryImpl
from users.infrastructure.notifications.sms import KavenegarSMSProvider
from users.infrastructure.notifications.email import DjangoEmailProvider

from users.application.commands.send_otp import SendOTPCommand
from users.application.commands.verify_otp import VerifyOTPCommand
from users.application.commands.register_email import RegisterEmailCommand
from users.application.commands.login_email import LoginEmailCommand
from users.application.commands.reset_password import ResetPasswordCommand
from users.application.commands.set_default_address import SetDefaultAddressCommand
from users.application.commands.cleanup_otp import CleanupOTPCommand
from users.application.queries.get_user_addresses import GetUserAddressesQuery

user_repo = UserRepositoryImpl()
otp_repo = OTPRepositoryImpl()
address_repo = AddressRepositoryImpl()

sms_provider = KavenegarSMSProvider()
email_provider = DjangoEmailProvider()

wait_minutes = getattr(settings, 'OTP_WAIT_TIME_MINUTES', 2)
max_daily = getattr(settings, 'OTP_MAX_DAILY_REQUESTS', 5)

send_otp_command = SendOTPCommand(otp_repo, sms_provider, email_provider, wait_minutes, max_daily)
verify_otp_command = VerifyOTPCommand(otp_repo, user_repo)
register_email_command = RegisterEmailCommand(user_repo)
login_email_command = LoginEmailCommand(user_repo)
reset_password_command = ResetPasswordCommand(otp_repo, user_repo)
set_default_address_command = SetDefaultAddressCommand(address_repo)
cleanup_otp_command = CleanupOTPCommand(otp_repo)

get_user_addresses_query = GetUserAddressesQuery(address_repo)
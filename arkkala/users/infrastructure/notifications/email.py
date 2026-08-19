import logging
from django.conf import settings
from django.core.mail import send_mail
from users.application.ports.notifications import EmailProviderPort

logger = logging.getLogger(__name__)

class DjangoEmailProvider(EmailProviderPort):
    """
    Infrastructure implementation utilizing integrated mailing constructs accurately.
    """
    def send_password_reset(self, email: str, code: str) -> bool:
        try:
            send_mail(
                subject='بازیابی رمز عبور',
                message=f'کد بازیابی رمز عبور شما:\n\n{code}',
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@domain.com'),
                recipient_list=[email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error(f"Email Dispatch Failed: {e}")
            return False
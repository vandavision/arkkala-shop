"""
Email Service for handling outgoing platform emails.
"""
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

class EmailService:
    """Service class to handle all email dispatches."""

    @staticmethod
    def send_order_invoice(order, user_email: str) -> bool:
        """
        Generates and sends an invoice email for a given order.
        """
        try:
            short_order_id = str(order.uuid).split('-')[0].upper()
            subject = f"فاکتور سفارش شماره {short_order_id} - {getattr(settings, 'SITE_NAME', 'ارک کالا')}"
            
            context = {
                'order': order,
                'short_id': short_order_id,
                'site_name': getattr(settings, 'SITE_NAME', 'ارک کالا'),
                'frontend_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            }
            
            html_message = render_to_string('emails/invoice_email.html', context)
            plain_message = strip_tags(html_message)
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@arkkala.com')
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=from_email,
                recipient_list=[user_email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Invoice email sent successfully to {user_email} for order {short_order_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send invoice email to {user_email}: {str(e)}")
            return False

    @staticmethod
    def send_custom_email(subject: str, template_name: str, context: dict, recipient_list: list) -> bool:
        """
        Generic method to send custom HTML emails.
        """
        try:
            html_message = render_to_string(template_name, context)
            plain_message = strip_tags(html_message)
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@arkkala.com')
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=from_email,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_list}: {str(e)}")
            return False
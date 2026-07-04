"""
Email Notification Service.
Used for sending invoices, welcome emails, and password resets.
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service to handle sending emails robustly."""

    @staticmethod
    def send_html_email(subject: str, template_name: str, context: dict, recipient_list: list[str]) -> bool:
        """
        Sends an HTML email using a Django template.
        
        Args:
            subject (str): Email subject.
            template_name (str): Path to the HTML template.
            context (dict): Data to pass to the template (like order details).
            recipient_list (list): List of recipient emails.
            
        Returns:
            bool: True if successful, False otherwise.
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
            logger.error(f"Failed to send email to {recipient_list}. Error: {str(e)}")
            return False

    @staticmethod
    def send_order_invoice(order, user_email: str) -> bool:
        """
        Helper method to send an invoice.
        """
        subject = f"فاکتور سفارش شماره {order.id} - ارک کالا"
        context = {
            'order': order,
            'user': order.user,
            'items': order.items.all()
        }
        return EmailService.send_html_email(subject, 'emails/invoice_email.html', context, [user_email])
#ifrom django.core.mail import send_mail
from django.conf import settings


def send_safe_mail(subject, message, recipient_list):
    """
    Send an email safely using Django's email backend.

    Args:
        subject (str): Email subject
        message (str): Email message body
        recipient_list (list): List of recipient email addresses

    Returns:
        int: Number of successfully sent emails
    """
    try:
        return send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
    except Exception as e:
        # Log the error but don't raise it to avoid breaking the application
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send email: {e}")
        return 0
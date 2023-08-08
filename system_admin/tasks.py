from celery import shared_task
from django.core.mail import send_mail

from SberBank.settings import EMAIL_HOST_USER


@shared_task
def send_email_to_ban_user(reason, email):
    send_mail(
        "Бан",
        f"Вы забанены в банке СберБанк!\nПричина: {reason}",
        EMAIL_HOST_USER,
        [email]
    )


@shared_task
def send_email_to_unban_user(email):
    send_mail(
        "Разбан",
        "Вы разбанены в банке СберБанк!",
        EMAIL_HOST_USER,
        [email]
    )

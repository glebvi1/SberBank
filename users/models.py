from smtplib import SMTPRecipientsRefused

from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models

from SberBank.settings import EMAIL_HOST_USER
from users import EV_SUBJECT, EV_HELLO_MESSAGE


class User(AbstractUser):
    patronymic = models.CharField(max_length=50, null=False, blank=False)
    code_for_reset_password = models.UUIDField(null=True, blank=True, default=None)
    # profile_image = models.ImageField(upload_to="users_images", blank=True, null=True)

    def __str__(self):
        return f"Логин: {self.username}"

    def __eq__(self, other):
        return self.username == other.username

    def get_FIO(self):
        return self.last_name + " " + self.first_name + " " + self.patronymic


class EmailVerification(models.Model):
    code = models.UUIDField(unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_finish = models.DateTimeField()
    is_verified = models.BooleanField(default=False)

    user = models.OneToOneField(to=User, on_delete=models.CASCADE)

    def send_email(self):
        subject = EV_SUBJECT
        link = f"http://127.0.0.1:8000/users/verification_email/{self.user.username}/{self.code}/"
        message = EV_HELLO_MESSAGE + link

        try:
            send_mail(
                subject,
                message,
                from_email=EMAIL_HOST_USER,
                recipient_list=[self.user.username]
            )
        except SMTPRecipientsRefused:
            pass

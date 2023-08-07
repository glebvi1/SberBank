import uuid
from datetime import timedelta

from celery import shared_task
from django.utils.timezone import now

from users.models import User, EmailVerification


@shared_task
def send_verification_email(user_id):
    user = User.objects.get(id=user_id)
    date_finish = now() + timedelta(days=1)
    code = uuid.uuid4()
    verification = EmailVerification.objects.create(user=user, code=code, date_finish=date_finish)
    verification.send_email()

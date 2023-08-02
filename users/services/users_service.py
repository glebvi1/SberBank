import uuid
from datetime import timedelta

from django.utils.timezone import now
from rolepermissions.roles import assign_role

from SberBank.roles import SimpleUser
from cards.services.cards_services import CardService
from chat.models import Room
from users.models import User, EmailVerification


class UserService:
    # TODO: подгрузка фотографии
    def registrate(self, user: User):
        """Функция присваивает пользователю карту, роль пользователя и отправляет верификационное письмо"""
        CardService().add_card_to_user(user, is_first=True)
        assign_role(user, SimpleUser)
        Room.objects.create(user=user)
        self.__send_verification_email(user.id)

    def __send_verification_email(self, user_id):
        user = User.objects.get(id=user_id)
        date_finish = now() + timedelta(days=1)
        code = uuid.uuid4()
        verification = EmailVerification.objects.create(user=user, code=code, date_finish=date_finish)
        verification.send_email()

    def verificate(self, email, code):
        user = User.objects.filter(username=email)
        if not user.exists():
            return False

        user = list(user)[0]
        email_verification = EmailVerification.objects.filter(code=code, user=user)

        if not email_verification.exists():
            return False

        email_verification = list(email_verification)[0]
        email_verification.is_verified = True
        email_verification.save()

        return True

    def reset_password(self, email, password):
        user = User.objects.get(username=email)
        user.code_for_reset_password = None
        user.set_password(password)
        user.save()

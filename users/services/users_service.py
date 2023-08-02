from rolepermissions.roles import assign_role

from SberBank.roles import SimpleUser
from cards.services.cards_services import CardService
from chat.models import Room
from users.models import User, EmailVerification
from users.tasks import send_verification_email


class UserService:
    # TODO: подгрузка фотографии
    def registrate(self, user: User):
        """Функция присваивает пользователю карту, роль пользователя и отправляет верификационное письмо"""
        CardService().add_card_to_user(user, is_first=True)
        assign_role(user, SimpleUser)
        Room.objects.create(user=user)
        send_verification_email.delay(user.id)

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

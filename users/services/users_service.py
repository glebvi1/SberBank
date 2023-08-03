import uuid
from datetime import timedelta

from django.utils.timezone import now
from rolepermissions.roles import assign_role

from SberBank.roles import SimpleUser
from cards.services.cards_services import CardService
from chat.models import Room
from users.models import EmailVerification, User


class UserService:
    # TODO: подгрузка фотографии
    def registrate(self, user: User) -> None:
        """Пользователю выдается первая карта с балансом 1млн Р, присваевается роль SimpleUser,
        создается чат с админом и отправляется верификационное письмо
        @param user: пользователь
        @return: None
        """
        CardService().add_card_to_user(user, is_first=True)
        assign_role(user, SimpleUser)
        Room.objects.create(user=user)
        self.__create_verification_email(user.id)

    def __create_verification_email(self, user_id: int) -> None:
        """Создание верификационнного письма
        @param user_id: id пользователя
        @return: None
        """
        user = User.objects.get(id=user_id)
        date_finish = now() + timedelta(days=1)
        code = uuid.uuid4()
        verification = EmailVerification.objects.create(user=user, code=code, date_finish=date_finish)
        verification.send_email()

    def verificate(self, email: str, code: str) -> bool:
        """Подтверждение почты
        @param email: почта
        @param code: код подтверждения
        @return: True, если подтверждение успешно, иначе - False
        """
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

    def reset_password(self, email: str, password: str) -> None:
        """Установка нового пароля
        @param email: почта пользователя
        @param password: новый пароль
        @return: None
        """
        user = User.objects.get(username=email)
        user.code_for_reset_password = None
        user.set_password(password)
        user.save()

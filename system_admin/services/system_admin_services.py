from django.core.mail import send_mail
from rolepermissions.roles import assign_role, clear_roles, remove_role

from SberBank.roles import BannedUser, SimpleUser
from SberBank.settings import EMAIL_HOST_USER
from system_admin.models import Ban
from users.models import User


class BanUserService:
    def ban_user(self, user_id, reason):
        user = User.objects.get(id=user_id)
        Ban.objects.create(banned_user=user, reason=reason)
        clear_roles(user)  # TODO: сохранить роли
        assign_role(user, BannedUser)

        send_mail(
            "Бан",
            f"Вы забанены в банке СберБанк!\nПричина: {reason}",
            EMAIL_HOST_USER,
            [user.username]
        )

    def unban(self, user_id):
        user = User.objects.get(id=user_id)
        remove_role(user, BannedUser)
        assign_role(user, SimpleUser)

        ban = Ban.objects.get(banned_user=user)
        ban.delete()

        send_mail(
            "Разбан",
            f"Вы разбанены в банке СберБанк!",
            EMAIL_HOST_USER,
            [user.username]
        )
        # TODO: Если до бана пользователь был VIPUser, то тут он теряет VIP...
        # TODO: Во время бана сохранять роли пользователя, здесь их просто возвращать

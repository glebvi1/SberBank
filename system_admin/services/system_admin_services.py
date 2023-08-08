from rolepermissions.roles import assign_role, remove_role

from SberBank.roles import BannedUser, SimpleUser
from system_admin.models import Ban
from system_admin.tasks import send_email_to_ban_user, send_email_to_unban_user
from users.models import User


class BanUserService:
    def ban_user(self, user_id, reason):
        user = User.objects.get(id=user_id)
        Ban.objects.create(banned_user=user, reason=reason)
        remove_role(user, SimpleUser)
        assign_role(user, BannedUser)

        send_email_to_ban_user.delay(reason, user.username)

    def unban(self, user_id):
        user = User.objects.get(id=user_id)
        remove_role(user, BannedUser)
        assign_role(user, SimpleUser)

        ban = Ban.objects.get(banned_user=user)
        ban.delete()

        send_email_to_unban_user.delay(user.username)

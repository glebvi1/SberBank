from django import forms
from rolepermissions.checkers import has_role

from SberBank.roles import SystemAdmin
from chat.models import Message
from users.models import User


class MessageForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={
        "placeholder": "Введите сообщение: ", "rows": "1", "cols": 30,
        "class": "form-control",
    }))

    def save(self, user, user_id):
        """ Функция сохраняет сообщение в БД
        @param user: пользователь, который сейчас в системе (может быть админом)
        @param user_id: пользователь, который точно не админ, "владлец" комнаты переговоров
        """
        is_admin = has_role(user, SystemAdmin)
        if is_admin:
            current_user = User.objects.get(id=user_id)
            room = current_user.room
            room.is_closed = True
        else:
            room = user.room
            room.is_closed = False

        room.save()
        Message.objects.create(text=self["text"].value(), room=room, is_admin=is_admin)

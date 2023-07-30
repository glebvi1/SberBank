from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from rolepermissions.checkers import has_role
from rolepermissions.mixins import HasRoleMixin

from SberBank import CARD_TEMPLATE_BASE, SYSTEM_ADMIN_TEMPLATE_BASE
from SberBank.roles import SimpleUser, BannedUser, SystemAdmin
from chat.forms import MessageForm
from chat.models import Message
from users.models import User


class ChatView(HasRoleMixin, FormView):
    allowed_roles = [BannedUser, SimpleUser, SystemAdmin]
    template_name = "chat/room.html"
    form_class = MessageForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if has_role(self.request.user, SimpleUser) or has_role(self.request.user, BannedUser):
            context["base"] = CARD_TEMPLATE_BASE
            context["is_admin"] = False
        elif has_role(self.request.user, SystemAdmin):
            context["base"] = SYSTEM_ADMIN_TEMPLATE_BASE
            context["is_admin"] = True

        room = User.objects.get(id=self.kwargs["user_id"]).room
        context["room"] = room
        context["messages"] = Message.objects.filter(room=room)

        return context

    def form_valid(self, form):
        form.save(self.request.user, self.kwargs["user_id"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("chat:room", kwargs={"user_id": self.kwargs["user_id"]})

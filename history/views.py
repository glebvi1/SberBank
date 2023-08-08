from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.list import ListView
from rolepermissions.checkers import has_role
from rolepermissions.mixins import HasRoleMixin

from SberBank import CARD_TEMPLATE_BASE
from SberBank.roles import BannedUser, SimpleUser, VIPUser
from cards.models import Card
from history.models import BaseTransactionHistory
from history.service.history_service import TransactionHistoryService
from vip_users.models import Category


@method_decorator(login_required, name="dispatch")
class CardHistoryListView(HasRoleMixin, ListView):
    allowed_roles = [BannedUser, SimpleUser, VIPUser]
    template_name = "history/history.html"
    model = BaseTransactionHistory
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        card = Card.objects.get(id=self.kwargs.get("card_id"))
        is_vip = has_role(self.request.user, VIPUser)

        context["card"] = card
        context["USER_TRANSACTION"] = BaseTransactionHistory.TYPE_TRANSACTION.USER
        context["CURRENCY_TRANSACTION"] = BaseTransactionHistory.TYPE_TRANSACTION.CURRENCY
        context["base"] = CARD_TEMPLATE_BASE
        context["is_admin"] = False
        context["is_vip"] = is_vip

        if "page" in self.kwargs:
            context["page"] = self.kwargs["page"]
        else:
            context["page"] = 1

        if is_vip:
            context["categories"] = Category.objects.filter(user=self.request.user)

        return context

    def get_queryset(self):
        card = Card.objects.get(id=self.kwargs.get("card_id"))
        return TransactionHistoryService().get_all_sort_transaction(card)

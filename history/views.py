from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from rolepermissions.mixins import HasRoleMixin

from SberBank import CARD_TEMPLATE_BASE
from SberBank.roles import SimpleUser, BannedUser
from cards.models import Card
from history.models import BaseTransactionHistory
from history.service.history_service import StatisticsService
from history.service.history_service import TransactionHistoryService


@method_decorator(login_required, name="dispatch")
class CardHistoryListView(HasRoleMixin, ListView):
    allowed_roles = [BannedUser, SimpleUser]
    template_name = "history/history.html"
    model = BaseTransactionHistory
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        card = Card.objects.get(id=self.kwargs.get("card_id"))
        context["card"] = card
        context["USER_TRANSACTION"] = BaseTransactionHistory.TYPE_TRANSACTION.USER
        context["CURRENCY_TRANSACTION"] = BaseTransactionHistory.TYPE_TRANSACTION.CURRENCY
        context["base"] = CARD_TEMPLATE_BASE
        context["is_admin"] = False

        return context

    def get_queryset(self):
        card = Card.objects.get(id=self.kwargs.get("card_id"))
        return TransactionHistoryService().get_all_sort_transaction(card)


@method_decorator(login_required, name="dispatch")
class StatisticsView(HasRoleMixin, TemplateView):
    allowed_roles = [BannedUser, SimpleUser]
    template_name = "history/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        card = Card.objects.get(id=context.get("card_id"))
        income_for_month, income_for_day, expense_for_month, expense_for_day = StatisticsService().get_statistics(card)

        context["card"] = card
        context["income_for_month"] = income_for_month
        context["income_for_day"] = income_for_day
        context["expense_for_month"] = expense_for_month
        context["expense_for_day"] = expense_for_day

        return context

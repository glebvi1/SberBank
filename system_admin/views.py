from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from rolepermissions.checkers import has_role
from rolepermissions.decorators import has_role_decorator
from rolepermissions.mixins import HasRoleMixin

from SberBank import SYSTEM_ADMIN_TEMPLATE_BASE
from SberBank.roles import BannedUser, SystemAdmin
from cards.models import Card
from cards.services.cards_services import CardService
from history.models import BaseTransactionHistory
from history.service.history_service import TransactionHistoryService
from system_admin.forms import (BanningUserForm, SearchUsersByEmailForm,
                                SearchUsersByFIOForm, SearchUsersByNumberForm)
from system_admin.services.system_admin_services import BanUserService
from users.models import User


@method_decorator(login_required, name="dispatch")
class UsersListView(HasRoleMixin, ListView):
    allowed_roles = [SystemAdmin]
    template_name = "system_admin/all_users.html"
    model = User
    paginate_by = 10

    def get_queryset(self):
        not_closed_users = User.objects.filter(room__is_closed=False)
        closed_users = User.objects.filter(room__is_closed=True).exclude(username=self.request.user.username)

        return list(not_closed_users)[::-1] + list(closed_users)


@method_decorator(login_required, name="dispatch")
class UserView(HasRoleMixin, FormView):
    allowed_roles = [SystemAdmin]
    template_name = "system_admin/user_view.html"
    form_class = BanningUserForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = User.objects.get(id=self.kwargs["user_id"])
        context["current_user"] = current_user
        context["cards"] = list(Card.objects.filter(user=current_user))
        context["is_banned"] = has_role(current_user, BannedUser)
        return context

    def form_valid(self, form):
        BanUserService().ban_user(self.kwargs["user_id"], form["text"].value())
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("system_admin:user_view", kwargs={"user_id": self.kwargs["user_id"]})


@method_decorator(login_required, name="dispatch")
class CardHistoryView(HasRoleMixin, ListView):
    allowed_roles = [SystemAdmin]
    template_name = "history/history.html"
    model = BaseTransactionHistory
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        card = Card.objects.get(id=self.kwargs.get("card_id"))
        current_user = User.objects.get(id=self.kwargs.get("user_id"))

        context["current_user"] = current_user
        context["card"] = card
        context["USER_TRANSACTION"] = BaseTransactionHistory.TYPE_TRANSACTION.USER
        context["CURRENCY_TRANSACTION"] = BaseTransactionHistory.TYPE_TRANSACTION.CURRENCY
        context["base"] = SYSTEM_ADMIN_TEMPLATE_BASE
        context["is_admin"] = True

        return context

    def get_queryset(self):
        card = Card.objects.get(id=self.kwargs.get("card_id"))
        return TransactionHistoryService().get_all_sort_transaction(card)


@login_required
@has_role_decorator(SystemAdmin)
def search_users(request):
    users = []
    form = None
    is_number_form, is_email_form, is_fio_form = False, False, False

    if request.method == "GET" and "type_search" in request.GET:
        if request.GET["type_search"] == "number":
            form = SearchUsersByNumberForm()
            is_number_form = True
        elif request.GET["type_search"] == "email":
            form = SearchUsersByEmailForm()
            is_email_form = True
        elif request.GET["type_search"] == "fio":
            form = SearchUsersByFIOForm()
            is_fio_form = True

    elif request.method == "POST" and "number_input" in request.POST:
        form = SearchUsersByNumberForm(data=request.POST)
        users = form.search() if form.is_valid() else []
    elif request.method == "POST" and "email_input" in request.POST:
        form = SearchUsersByEmailForm(data=request.POST)
        users = form.search() if form.is_valid() else []
    elif request.method == "POST" and "fio_input" in request.POST:
        form = SearchUsersByFIOForm(data=request.POST)
        users = form.search() if form.is_valid() else []

    if request.method == "POST" and len(users) == 0:
        messages.error(request, "Таких пользователей не существует!")

    context = {
        "users": users,
        "form": form,
        "is_number_form": is_number_form,
        "is_email_form": is_email_form,
        "is_fio_form": is_fio_form,
    }

    return render(request, "system_admin/search_users.html", context)


@login_required
@has_role_decorator(SystemAdmin)
def unban(request, user_id):
    BanUserService().unban(user_id)
    return HttpResponseRedirect(reverse("system_admin:user_view", args=(user_id,)))


@login_required
@has_role_decorator(SystemAdmin)
def add_card(request, user_id):
    CardService().add_card_to_user(User.objects.get(id=user_id))
    return HttpResponseRedirect(reverse("system_admin:user_view", args=(user_id,)))

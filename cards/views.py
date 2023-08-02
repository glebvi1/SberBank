from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from rolepermissions.checkers import has_role
from rolepermissions.decorators import has_role_decorator
from rolepermissions.mixins import HasRoleMixin

from SberBank.roles import BannedUser, SimpleUser
from cards.forms import TransferMoneyByNumberForm
from cards.models import Card
from cards.services.cards_services import ParseService, TransferService


@login_required
@has_role_decorator([BannedUser, SimpleUser])
def my_card(request, card_id):
    card = Card.objects.get(id=card_id)
    is_confirm = False
    confirm_message = ""
    card_transfer = None
    is_banned = has_role(request.user, BannedUser)

    if request.method == "POST" and "input_translate_from" in request.POST and not is_banned:
        form = TransferMoneyByNumberForm(data=request.POST)
        summa = int(form["summa"].value())
        number = form["number"].value()

        if form.is_valid():
            confirm_message, card_transfer = TransferService().check_transfer_by_number(card, summa, number)
            is_confirm = not (card_transfer is None)

    elif request.method == "POST" and "confirm_translate_form" in request.POST and not is_banned:
        form = TransferMoneyByNumberForm(data=request.POST)
        summa = int(form["summa"].value())
        number = form["number"].value()

        card2 = Card.objects.get(number=number)
        TransferService().transfer(card, card2, summa)
        messages.success(request, "Операция успешна!")

        form = TransferMoneyByNumberForm()
    else:
        form = TransferMoneyByNumberForm()

    context = {
        "card": card,
        "form": form,
        "is_confirm": is_confirm,
        "confirm_message": confirm_message,
        "card_transfer": card_transfer,
        "is_banned": is_banned,
    }

    return render(request, "cards/my_card.html", context)


@method_decorator(login_required, name="dispatch")
class CurrenciesView(HasRoleMixin, TemplateView):
    allowed_roles = [SimpleUser]
    template_name = "cards/currency.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        card = Card.objects.get(id=context.get("card_id"))
        context["card"] = card
        context["currencies"] = ParseService().parse_course(card.currency)
        return context


@login_required
@has_role_decorator(SimpleUser)
def transfer_currency(request, card_id, currency):
    card1 = Card.objects.get(id=card_id)
    TransferService().transfer_currency(card1, currency)
    return HttpResponseRedirect(reverse("cards:my_card", args=(card_id,)))

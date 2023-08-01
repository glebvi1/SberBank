from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.list import ListView
from rolepermissions.checkers import has_role
from rolepermissions.decorators import has_role_decorator
from rolepermissions.mixins import HasRoleMixin

from SberBank.roles import VIPUser, SimpleUser
from cards.models import Card
from vip_users.forms import CategoryCreateForm
from vip_users.models import Category
from vip_users.services.vip_services import VIPService


@login_required
@has_role_decorator([SimpleUser])
def buy_vip(request):
    if has_role(request.user, VIPUser):
        messages.error(request, "Вы уже VIP пользователь!")
        return HttpResponseRedirect(reverse("users:account"))
    context = {"cards": Card.objects.filter(user=request.user)}

    if request.method == "POST":
        print(request.POST["card_id"])
        card_id = request.POST["card_id"]
        message, is_ok = VIPService().buy_vip(request.user, card_id)
        if is_ok:
            messages.success(request, "Поздравляем, Вы преобрели VIP-подписку!")
            return HttpResponseRedirect(reverse("users:account"))
        else:
            messages.error(request, message)
            return render(request, "vip_users/buy_vip.html", context)

    return render(request, "vip_users/buy_vip.html", context)


@login_required
@has_role_decorator(VIPUser)
def create_category(request):
    if request.method == "POST":
        form = CategoryCreateForm(data=request.POST)
        if form.is_valid():
            if Category.objects.filter(user=request.user, name=form["name"].value()).exists():
                messages.error(request, "Категория с таким названием уже существует!")
                return render(request, "vip_users/create_category.html", {"form": form})
            form = form.save(commit=False)
            form.user = request.user
            form.save()
            return HttpResponseRedirect(reverse("vip_users:all_categories"))
    else:
        form = CategoryCreateForm()

    return render(request, "vip_users/create_category.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class CategoriesListView(HasRoleMixin, ListView):
    allowed_roles = [VIPUser]
    template_name = "vip_users/all_categories.html"
    model = Category

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


@login_required
@has_role_decorator(VIPUser)
def bind_transaction(request, card_id, transaction_id):
    if request.method == "POST":
        print(request.POST)
        print(request.POST[f"select{transaction_id}"])
    return HttpResponseRedirect(reverse("history:card_history", args=(card_id,)))

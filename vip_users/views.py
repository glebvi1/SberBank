from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, UpdateView
from django.views.generic.list import ListView
from rolepermissions.checkers import has_role
from rolepermissions.decorators import has_role_decorator
from rolepermissions.mixins import HasRoleMixin

from SberBank.roles import SimpleUser, VIPUser
from cards.models import Card
from vip_users.forms import CategoryCreateForm
from vip_users.models import Category
from vip_users.services.vip_services import (StatisticsService, VIPService,
                                             get_nearest_month_and_year)


@login_required
@has_role_decorator([SimpleUser])
def buy_vip(request):
    if has_role(request.user, VIPUser):
        messages.error(request, "Вы уже VIP пользователь!")
        return HttpResponseRedirect(reverse("users:account"))
    context = {"cards": Card.objects.filter(user=request.user),}

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
            if not VIPService().check_create_category(request.user, form["name"].value()):
                messages.error(request, "Категория с таким названием уже существует!")
                return render(request, "vip_users/create_category.html", {"form": form})
            form = form.save(commit=False)
            form.user = request.user
            form.save()
            return HttpResponseRedirect(reverse("vip_users:all_categories"))
    else:
        form = CategoryCreateForm()

    context = {
        "form": form,
        "month": datetime.now().month,
        "year": datetime.now().year,
        "is_create": True,
    }

    return render(request, "vip_users/create_category.html", context)


@method_decorator(login_required, name="dispatch")
class CategoriesListView(HasRoleMixin, ListView):
    allowed_roles = [VIPUser]
    template_name = "vip_users/all_categories.html"
    model = Category

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["month"] = datetime.now().month
        context["year"] = datetime.now().year

        return context

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


@login_required
@has_role_decorator(VIPUser)
def bind_transaction(request, card_id, transaction_id):
    if request.method == "POST":
        category_id = request.POST[f"select{transaction_id}"]
        if not category_id == "None":
            VIPService().add_category_to_transaction(category_id, transaction_id)
    return HttpResponseRedirect(reverse("history:card_history", args=(card_id,)))


@method_decorator(login_required, name="dispatch")
class MonthStatisticsCategory(HasRoleMixin, TemplateView):
    allowed_roles = [VIPUser]
    template_name = "vip_users/global_statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        month = self.kwargs["month"]
        year = self.kwargs["year"]

        statistics_plus, statistics_neg = StatisticsService() \
            .get_global_statistics_for_month(self.request.user, month, year)

        context["statistics_plus"] = statistics_plus
        context["statistics_neg"] = statistics_neg

        context["pred_month"], context["next_month"], context["pred_year"], context["next_year"] = \
            get_nearest_month_and_year(month, year)

        return context


@method_decorator(login_required, name="dispatch")
class StatisticsForCategory(HasRoleMixin, TemplateView):
    allowed_roles = [VIPUser]
    template_name = "vip_users/category_statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month = self.kwargs["month"]
        year = self.kwargs["year"]

        category = Category.objects.get(id=self.kwargs["category_id"])
        context["statistic"] = StatisticsService().get_statistics_for_category(self.request.user, category, month, year)

        context["pred_month"], context["next_month"], context["pred_year"], context["next_year"] = \
            get_nearest_month_and_year(month, year)

        return context


@method_decorator(login_required, name="dispatch")
class CategoryEditView(HasRoleMixin, UpdateView):
    allowed_roles = [VIPUser]
    form_class = CategoryCreateForm
    template_name = "vip_users/create_category.html"
    model = Category
    success_url = reverse_lazy("vip_users:all_categories")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["month"] = datetime.now().month
        context["year"] = datetime.now().year
        context["is_create"] = False

        return context

    def form_valid(self, form):
        if not VIPService().check_update_category(self.request.user, form["name"].value(), self.kwargs["pk"]):
            messages.error(self.request, "Категория с таким названием уже существует!")
            return HttpResponseRedirect(reverse("vip_users:edit_category", args=(self.kwargs["pk"],)))
        form.save()
        return HttpResponseRedirect(reverse("vip_users:all_categories"))


@login_required
@has_role_decorator(VIPUser)
def delete_category(request, pk):
    VIPService().delete_category(pk)
    return HttpResponseRedirect(reverse("vip_users:all_categories"))

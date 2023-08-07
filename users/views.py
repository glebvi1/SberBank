from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, FormView
from django.views.generic.list import ListView
from rolepermissions.checkers import has_role
from rolepermissions.mixins import HasRoleMixin

from SberBank import CARD_TEMPLATE_BASE, SYSTEM_ADMIN_TEMPLATE_BASE
from SberBank.roles import BannedUser, SimpleUser, SystemAdmin, VIPUser
from cards.models import Card
from users.forms import (ForgotPasswordForm, ResetPasswordForm, UserLoginForm,
                         UserRegistrationForm)
from users.models import User
from users.services.users_service import UserService


@method_decorator(login_required, name="dispatch")
class AccountView(HasRoleMixin, ListView):
    allowed_roles = [BannedUser, SimpleUser, SystemAdmin]
    template_name = "users/account.html"
    model = Card

    def get_queryset(self):
        return self.request.user.card_set.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if has_role(self.request.user, SystemAdmin):
            context["base"] = SYSTEM_ADMIN_TEMPLATE_BASE
        elif has_role(self.request.user, SimpleUser) or has_role(self.request.user, BannedUser):
            context["base"] = CARD_TEMPLATE_BASE
        if has_role(self.request.user, VIPUser):
            context["month"] = datetime.now().month
            context["year"] = datetime.now().year

        return context


class UserLoginView(LoginView):
    template_name = "users/login.html"
    form_class = UserLoginForm

    def form_valid(self, form):
        user = form.get_user()
        if user.emailverification.is_verified:
            return super().form_valid(form)
        else:
            messages.error(self.request, "Вы не подтвердили почту!")
            context = {"form": form}
            return render(self.request, self.template_name, context)


class RegistrationView(SuccessMessageMixin, CreateView):
    template_name = "users/registration.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("users:login")
    success_message = "Регистрация успешна! Подтвердите указаную почту."


class EmailVerificationView(TemplateView):
    template_name = "users/verification_email.html"

    def get(self, request, *args, **kwargs):
        if UserService().verificate(kwargs["email"], kwargs["code"]):
            return super(EmailVerificationView, self).get(request, *args, **kwargs)
        return HttpResponseRedirect(reverse("users:login"))


class ForgotPasswordView(FormView):
    template_name = "users/forgot_password.html"
    form_class = ForgotPasswordForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        if form.send_email(form["email"].value()):
            messages.success(self.request, "Вам на почту пришло письмо")
            return super().form_valid(form)

        messages.error(self.request, "Пользователя с такой почтой не существует. Проверьте введенную почту")
        return render(self.request, self.template_name)


class ResetPasswordView(FormView):
    template_name = "users/reset_password.html"
    form_class = ResetPasswordForm
    success_url = reverse_lazy("users:login")

    def get(self, request, *args, **kwargs):
        if User.objects.filter(username=kwargs["email"], code_for_reset_password=kwargs["code"]).exists():
            return super(ResetPasswordView, self).get(request, *args, **kwargs)
        return HttpResponseRedirect(reverse("users:login"))

    def form_valid(self, form):
        if form["password1"].value() == form["password2"].value():
            UserService().reset_password(self.kwargs["email"], form["password1"].value())
            messages.success(self.request, "Пароль успешно изменен!")
            return super().form_valid(form)

        messages.error(self.request, "Пароли не совпадают")
        context = {
            "email": self.kwargs["email"],
            "code": self.kwargs["code"],
            "form": self.get_form(),
        }
        return render(self.request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["email"] = self.kwargs["email"]
        context["code"] = self.kwargs["code"]
        return context

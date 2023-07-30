from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.mail import send_mail
from SberBank.settings import EMAIL_HOST_USER
import uuid
from users.models import User
from users.services.users_service import UserService
from captcha.fields import CaptchaField


class UserLoginForm(AuthenticationForm):

    username = forms.CharField(widget=forms.EmailInput(attrs={
        "placeholder": "Введите почту: "
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "placeholder": "Введите пароль: "
    }))

    class Meta:
        model = User
        fields = ("username", "password")


class UserRegistrationForm(UserCreationForm):

    first_name = forms.CharField(widget=forms.TextInput(attrs={
        "placeholder": "Введите своё имя: "
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        "placeholder": "Введите свою фамилию: "
    }))
    patronymic = forms.CharField(widget=forms.TextInput(attrs={
        "placeholder": "Введите своё отчество: "
    }))
    username = forms.CharField(widget=forms.EmailInput(attrs={
        "placeholder": "Введите почту: "
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        "placeholder": "Введите пароль: "
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        "placeholder": "Введите пароль ещё раз: "
    }))

    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ("first_name", "last_name", "patronymic", "username", "password1", "password2")

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=True)
        UserService().registrate(user)
        return user


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        "placeholder": "Введите свою почту: "
    }))

    def send_email(self, email) -> bool:
        user = User.objects.filter(username=email)
        if not user.exists():
            return False

        user = list(user)[0]
        user.code_for_reset_password = uuid.uuid4()
        user.save()

        link = f"http://127.0.0.1:8000/users/reset_password/{email}/{user.code_for_reset_password}/"
        send_mail(
            "Сброс пароля",
            f"Чтобы сбросить пароль, перейдите по ссылке: {link}",
            EMAIL_HOST_USER,
            [email]
        )

        return True


class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        "placeholder": "Введите пароль: "
    }))

    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        "placeholder": "Введите пароль ещё раз: "
    }))

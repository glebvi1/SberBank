from django import forms

from cards.models import Card
from users.models import User


class SearchUsersByNumberForm(forms.Form):
    number = forms.CharField(widget=forms.TextInput(attrs={
        "placeholder": "Введите номер: "
    }))

    def search(self):
        card = Card.objects.filter(number=self["number"].value())
        if card.exists():
            return [card.first().user]
        return []


class SearchUsersByEmailForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        "placeholder": "Введите свою почту: "
    }))

    def search(self):
        users = User.objects.filter(username=self["email"].value())
        if users.exists():
            return users
        return []


class SearchUsersByFIOForm(forms.Form):
    name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "placeholder": "Введите имя: "
    }))

    surname = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "placeholder": "Введите фамилию: "
    }))

    patronymic = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "placeholder": "Введите отчество: "
    }))

    def search(self):
        name = self["name"].value()
        surname = self["surname"].value()
        patronymic = self["patronymic"].value()
        return User.objects.filter(first_name=name, last_name=surname, patronymic=patronymic)


class BanningUserForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={
        "placeholder": "Введите причину бана: ", "rows": "1", "cols": 30,
    }))

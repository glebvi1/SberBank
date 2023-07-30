from django import forms


class TransferMoneyByNumberForm(forms.Form):

    number = forms.CharField(widget=forms.TextInput(attrs={
        "placeholder": "Введите номер карты: "
    }))

    summa = forms.IntegerField(widget=forms.NumberInput(attrs={
        "placeholder": "Введите сумму перевода: "
    }))

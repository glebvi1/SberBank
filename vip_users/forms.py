from django import forms

from vip_users.models import Category


class CategoryCreateForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={
        "placeholder": "Введите название: "
    }))

    description = forms.CharField(widget=forms.TextInput(attrs={
        "placeholder": "Введите описание: : "
    }))

    class Meta:
        model = Category
        exclude = ["user"]

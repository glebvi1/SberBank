import decimal

from django.template.defaulttags import register

from cards.models import Card


@register.filter
def round_balance(balance, rate):
    return round(decimal.Decimal(balance) / rate, 2)


@register.filter
def my_round(balance):
    return round(decimal.Decimal(balance), 2)


@register.filter
def currency_to_view(currency):
    return Card.CURRENCY(currency).to_view()

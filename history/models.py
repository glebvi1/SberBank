from datetime import datetime

from django.db import models
from django.utils.translation import gettext_lazy

from cards.models import Card
from vip_users.models import Category


class BaseTransactionHistory(models.Model):
    class TYPE_TRANSACTION(models.IntegerChoices):
        USER = 1, gettext_lazy("UserTransaction")
        CURRENCY = 2, gettext_lazy("CurrencyTransaction")

    time = models.DateTimeField(default=datetime.now)
    summa = models.FloatField(blank=False, null=False)
    currency = models.CharField(max_length=3, choices=Card.CURRENCY.choices)
    type_transaction = models.SmallIntegerField(choices=TYPE_TRANSACTION.choices, blank=False, null=False)


class UserTransactionHistory(BaseTransactionHistory):
    card = models.ForeignKey(to=Card, on_delete=models.CASCADE, related_name="expense_transaction")
    card_transaction = models.ForeignKey(to=Card, on_delete=models.CASCADE, related_name="income_transactions")
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, null=True, blank=True, default=None)


class CurrencyTransactionHistory(BaseTransactionHistory):
    card = models.ForeignKey(to=Card, on_delete=models.CASCADE, related_name="currency_transactions")
    currency_after_transaction = models.CharField(max_length=3, choices=Card.CURRENCY.choices)
    rate = models.FloatField(blank=False, null=False)

    def __str__(self):
        x = round(float(self.summa) / float(self.rate), 2)
        return f"{self.summa} {self.currency} -> {x} {self.currency_after_transaction}"

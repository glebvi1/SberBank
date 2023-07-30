from django.db import models
from cards.models import Card
from django.utils.translation import gettext_lazy


class BaseTransactionHistory(models.Model):
    class TYPE_TRANSACTION(models.IntegerChoices):
        USER = 1, gettext_lazy("UserTransaction")
        CURRENCY = 2, gettext_lazy("CurrencyTransaction")

    time = models.DateTimeField(auto_now=True)
    summa = models.FloatField(blank=False, null=False)
    currency = models.CharField(max_length=3, choices=Card.CURRENCY.choices)
    type_transaction = models.SmallIntegerField(choices=TYPE_TRANSACTION.choices, blank=False, null=False)


class UserTransactionHistory(BaseTransactionHistory):
    card = models.ForeignKey(to=Card, on_delete=models.CASCADE, related_name="expense_transaction")
    card_transaction = models.ForeignKey(to=Card, on_delete=models.CASCADE, related_name="income_transactions")


class CurrencyTransactionHistory(BaseTransactionHistory):
    card = models.ForeignKey(to=Card, on_delete=models.CASCADE, related_name="currency_transactions")
    currency_after_transaction = models.CharField(max_length=3, choices=Card.CURRENCY.choices)
    rate = models.FloatField(blank=False, null=False)


    def __str__(self):
        x = round(float(self.summa) / float(self.rate), 2)
        return f"{self.summa} {self.currency} -> {x} {self.currency_after_transaction}"

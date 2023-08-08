from django.db import models
from django.utils.translation import gettext_lazy

from users.models import User


class Card(models.Model):
    class CURRENCY(models.TextChoices):
        RUBLE = "RUS", gettext_lazy("Рубль")
        DOLLAR = "USD", gettext_lazy("Доллар")
        EURO = "EUR", gettext_lazy("Евро")
        YUAN = "CNY", gettext_lazy("Юань")

        def to_view(self):
            return CURRENCY_TO_VIEW[self.value]

    currency = models.CharField(max_length=3, choices=CURRENCY.choices, default=CURRENCY.RUBLE)
    number = models.CharField(max_length=16, null=False, blank=False, unique=True)
    balance = models.DecimalField(null=False, blank=False, max_digits=19, decimal_places=10)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def number_to_view(self):
        current_number = str(self.number)
        number_to_view = ""

        for i in range(len(current_number)):
            number_to_view += current_number[i]
            if (i+1) % 4 == 0 and i != 15:
                number_to_view += "-"

        return number_to_view

    def currency_to_view(self) -> str:
        return CURRENCY_TO_VIEW[self.currency]

    def balance_to_view(self):
        return round(self.balance, 2)

    def __eq__(self, other):
        return self.id == other.id


CURRENCY_TO_VIEW = {
    Card.CURRENCY.RUBLE: "₽",
    Card.CURRENCY.DOLLAR: "$",
    Card.CURRENCY.EURO: "€",
    Card.CURRENCY.YUAN: "¥",
}

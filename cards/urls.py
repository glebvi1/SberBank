from django.urls import path

from cards.views import CurrenciesView, my_card, transfer_currency

app_name = "cards"

urlpatterns = [
    path("my_card/<int:card_id>/", my_card, name="my_card"),
    path("my_card/<int:card_id>/currencies/", CurrenciesView.as_view(), name="currencies"),
    path("my_card/<int:card_id>/currencies/<str:currency>/", transfer_currency, name="transfer_currency"),
]

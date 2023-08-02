import random

import requests
from django.core.mail import send_mail
from rolepermissions.checkers import has_role

from SberBank.roles import BannedUser, VIPUser
from SberBank.settings import EMAIL_HOST_USER
from cards import (MESSAGE_BAN_USER, MESSAGE_CONFIRM, MESSAGE_EXIST_CARD,
                   MESSAGE_MYSELF_TRANSFER, MESSAGE_NOT_ENOUGH_BALANCE,
                   MESSAGE_NOT_EQ_CURRENCY)
from cards.models import CURRENCY_TO_VIEW, Card
from history.models import CurrencyTransactionHistory, UserTransactionHistory


class CardService:
    def add_card_to_user(self, user, is_first=False) -> None:
        card = Card(user=user, currency=Card.CURRENCY.RUBLE, number=self.__generate_unique_card_number())
        card.balance = 1000000 if is_first else 0
        card.save()

    def __generate_unique_card_number(self) -> str:
        number = ""
        for _ in range(16):
            number += str(random.randint(0, 9))

        while Card.objects.filter(number=number).exists():
            number = ""
            for _ in range(16):
                number += str(random.randint(0, 9))

        return number


class TransferService:
    def __send_mail_to_user_income(self, transaction: UserTransactionHistory):
        if has_role(transaction.card_transaction.user, VIPUser):
            send_mail(
                "Поступление денег",
                f"Вам перевели {transaction.summa} {transaction.card.currency_to_view()}."
                f"\nОт: {transaction.card.user.get_FIO()}",
                EMAIL_HOST_USER,
                [transaction.card_transaction.user.username]
            )

    def __send_mail_to_user_expense(self, transaction: UserTransactionHistory):
        if has_role(transaction.card.user, VIPUser):
            send_mail(
                "Списание денег",
                f"Вы перевели {transaction.summa} {transaction.card.currency_to_view()}."
                f"\nПолучатель: {transaction.card_transaction.user.get_FIO()}",
                EMAIL_HOST_USER,
                [transaction.card.user.username]
            )

    def __send_mail_to_user_currency(self, transaction: CurrencyTransactionHistory):
        if has_role(transaction.card.user, VIPUser):
            currency_after_transaction_view = transaction.card.currency_to_view()
            currency_view = CURRENCY_TO_VIEW[transaction.currency]
            send_mail(
                "Перевод валюты",
                f"Вы перевели {round(transaction.summa, 2)} {currency_view} = "
                f"{round(transaction.summa / transaction.rate, 2)} {currency_after_transaction_view}."
                f"\nПо курсу: 1 {currency_view} = {round(transaction.rate, 2)} {currency_after_transaction_view}",
                EMAIL_HOST_USER,
                [transaction.card.user.username]
            )

    def transfer_currency(self, card, currency):
        transaction = CurrencyTransactionHistory(card=card, summa=card.balance, currency=card.currency,
                                                 currency_after_transaction=currency, type_transaction=2)

        rate = self.__get_rate_by_currency(card, currency)
        card.balance = card.balance / rate
        card.currency = currency
        transaction.rate = rate

        card.save()
        transaction.save()

        self.__send_mail_to_user_currency(transaction)

    def transfer(self, card1, card2, summa):
        """
        card1: карта, из которой снимают деньги
        card2: карта, на которую переводят
        """

        transaction = UserTransactionHistory(card=card1, summa=summa, currency=card1.currency,
                                             card_transaction=card2, type_transaction=1)

        card1.balance -= summa
        card2.balance += summa

        transaction.save()
        card1.save()
        card2.save()

        self.__send_mail_to_user_expense(transaction)
        self.__send_mail_to_user_income(transaction)

    def check_transfer_by_number(self, card, summa, number) -> tuple:
        card_transfer = Card.objects.filter(number=number)

        if not card_transfer.exists():
            return MESSAGE_EXIST_CARD, None

        card_transfer = list(card_transfer)[0]
        is_eq_currency = card_transfer.currency == card.currency
        is_myself = card.number == number

        if has_role(card_transfer.user, BannedUser):
            return MESSAGE_BAN_USER, None

        if not self.__check_transfer(card, summa):
            return MESSAGE_NOT_ENOUGH_BALANCE, None

        if is_myself:
            return MESSAGE_MYSELF_TRANSFER, None

        if not is_eq_currency:
            return MESSAGE_NOT_EQ_CURRENCY, None
        return MESSAGE_CONFIRM, card_transfer

    def __get_rate_by_currency(self, card, currency):
        return ParseService().parse_course(card.currency)[currency]

    def __check_transfer(self, card: Card, summa: int):
        return 0 < summa <= card.balance


class ParseService:
    def parse_course(self, current_currency) -> dict:
        data_rate = requests.get("https://www.cbr-xml-daily.ru/daily_json.js").json()

        x = {}

        for name in CURRENCY_TO_VIEW.keys():
            if name == Card.CURRENCY.RUBLE:
                x[name] = 1
            else:
                x[name] = data_rate["Valute"][name]["Value"]

        rate_to_ruble = x[current_currency]
        result = {}

        for key, value in x.items():
            if key == current_currency:
                continue
            result[key] = value / rate_to_ruble

        return result

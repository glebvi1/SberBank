import random
from typing import Optional, Tuple

import requests
from rolepermissions.checkers import has_role

from SberBank.roles import BannedUser, VIPUser
from cards import (MESSAGE_BAN_USER, MESSAGE_CONFIRM, MESSAGE_EXIST_CARD,
                   MESSAGE_MYSELF_TRANSFER, MESSAGE_NOT_ENOUGH_BALANCE,
                   MESSAGE_NOT_EQ_CURRENCY, RATE_URL, START_BALANCE)
from cards.models import CURRENCY_TO_VIEW, Card
from cards.tasks import send_email_to_user_income, send_email_to_user_expense, send_email_to_user_currency, \
    send_email_to_user_add_card
from history.models import (BaseTransactionHistory, CurrencyTransactionHistory,
                            UserTransactionHistory)
from users.models import User


class CardService:
    def add_card_to_user(self, user: User, is_first=False) -> None:
        """
        @param user: пользователь, которому добавляется карта
        @param is_first: первая ли эта карта у user? Если нет, то баланс на карте = 0, иначе - START_BALANCE Р
        @return: None
        """
        card = Card(user=user, currency=Card.CURRENCY.RUBLE, number=self.__generate_unique_card_number())
        card.balance = START_BALANCE if is_first else 0
        card.save()

        if not is_first:
            send_email_to_user_add_card.delay(card.number, user.username)

    def __generate_unique_card_number(self) -> str:
        """Генерирует уникальный 16-значный номер карты
        @return: Номер (str)
        """
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
            send_email_to_user_income.delay(fio=transaction.card.user.get_FIO(),
                                            summa=transaction.summa,
                                            currency_to_view=transaction.card.currency_to_view(),
                                            email=transaction.card_transaction.user.username)

    def __send_mail_to_user_expense(self, transaction: UserTransactionHistory):
        if has_role(transaction.card.user, VIPUser):
            send_email_to_user_expense.delay(fio=transaction.card_transaction.user.get_FIO(),
                                             summa=transaction.summa,
                                             currency_to_view=transaction.card.currency_to_view(),
                                             email=transaction.card.user.username)

    def __send_mail_to_user_currency(self, transaction: CurrencyTransactionHistory):
        if has_role(transaction.card.user, VIPUser):
            currency_after_transaction_view = transaction.card.currency_to_view()
            currency_view = CURRENCY_TO_VIEW[transaction.currency]
            send_email_to_user_currency.delay(summa=transaction.summa,
                                              rate=transaction.rate,
                                              currency_view=currency_view,
                                              currency_after_transaction_view=currency_after_transaction_view,
                                              email=transaction.card.user.username)

    def transfer_currency(self, card_id: int, currency: str) -> None:
        """Перевод валюты карты в другую валюту
        @param card_id: id карты, с которой осуществляется перевод
        @param currency: валюта, в которую переводятся деньги
        @return: None
        """
        card = Card.objects.get(id=card_id)
        transaction = CurrencyTransactionHistory(card=card, summa=card.balance, currency=card.currency,
                                                 currency_after_transaction=currency, type_transaction=2)

        rate = self.__get_rate_by_currency(card, currency)
        card.balance = card.balance / rate
        card.currency = currency
        transaction.rate = rate
        card.save()
        transaction.save()

        self.__send_mail_to_user_currency(transaction)

    def transfer(self, card1: Card, card2: Card, summa: int) -> None:
        """Перевод между двумя картами
        @param card1: карта, из которой снимают деньги
        @param card2: карта, на которую переводят
        @param summa: сумма денег, которую переводят
        @return: None
        """

        transaction = UserTransactionHistory(card=card1, summa=summa, currency=card1.currency,
                                             card_transaction=card2, type_transaction=BaseTransactionHistory.TYPE_TRANSACTION.USER)

        card1.balance -= summa
        card2.balance += summa

        transaction.save()
        card1.save()
        card2.save()

        self.__send_mail_to_user_expense(transaction)
        self.__send_mail_to_user_income(transaction)

    def check_transfer_by_number(self, card: Card, summa: int, number: str) -> Tuple[str, Optional[Card]]:
        """Проверка номера, на который будет совершаться перевод
        @param card: карта, с которой будут сниматься деньги
        @param summa: сумма перевода
        @param number: номер получателя
        @return: Tuple[str, Optional[Card]]
        """
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

    def check_transfer_currency(self, card_id, currency) -> bool:
        """Проверка перовода валюты
        @param card_id: id карты
        @return: True - проверка успешна, False - иначе
        """
        card = Card.objects.get(id=card_id)
        if card.balance < 1000 or has_role(card.user, BannedUser) or card.currency == currency:
            return False
        return True

    def __get_rate_by_currency(self, card, currency):
        return ParseService().parse_course(card.currency)[currency]

    def __check_transfer(self, card: Card, summa: int):
        return 0 < summa <= card.balance


class ParseService:
    def parse_course(self, current_currency) -> dict:
        data_rate = requests.get(RATE_URL).json()

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

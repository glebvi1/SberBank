from http import HTTPStatus

import requests
from django.test import TestCase
from rolepermissions.roles import assign_role

from SberBank.roles import BannedUser
from cards import (MESSAGE_BAN_USER, MESSAGE_CONFIRM, MESSAGE_EXIST_CARD,
                   MESSAGE_MYSELF_TRANSFER, MESSAGE_NOT_ENOUGH_BALANCE,
                   MESSAGE_NOT_EQ_CURRENCY, RATE_URL, START_BALANCE)
from cards.models import Card
from cards.services.cards_services import (CardService, ParseService,
                                           TransferService)
from history.models import BaseTransactionHistory, UserTransactionHistory
from users.models import User


class CardServiceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(first_name="Глеб", last_name="Глебов", patronymic="Глебович",
                            username="gleb@mail.ru")

    def test_add_card_to_user_first(self):
        """Проверка добавления карты, если карта первая"""
        user = User.objects.get(username="gleb@mail.ru")
        CardService().add_card_to_user(user, is_first=True)
        user_cards = Card.objects.filter(user=user)

        self.assertEquals(user_cards.count(), 1)
        card = user_cards.first()
        self.assertEquals(card.balance, START_BALANCE)
        self.assertEquals(card.currency, Card.CURRENCY.RUBLE)

    def test_add_card_to_user_not_first(self):
        """Проверка добавления карты. Не первой"""
        user = User.objects.get(username="gleb@mail.ru")
        CardService().add_card_to_user(user, is_first=True)
        CardService().add_card_to_user(user, is_first=False)
        user_cards = Card.objects.filter(user=user)

        self.assertTrue(user_cards.count() == 2)
        card = user_cards.last()
        self.assertEquals(card.balance, 0)
        self.assertEquals(card.currency, Card.CURRENCY.RUBLE)


class TransferServiceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user1 = User.objects.create(first_name="Иван", last_name="Иванов", patronymic="Иванович",
                                    username="ivan@mail.ru")
        user2 = User.objects.create(first_name="Петр", last_name="Петров", patronymic="Петрович",
                                    username="petr@mail.ru")
        user3 = User.objects.create(first_name="Глеб", last_name="Глебов", patronymic="Глебович",
                                    username="gleb@mail.ru")
        assign_role(user3, BannedUser)
        Card.objects.create(
            number="0000111122223333",
            currency=Card.CURRENCY.RUBLE,
            balance=1000,
            user=user1,
        )
        Card.objects.create(
            number="4444555566667777",
            currency=Card.CURRENCY.DOLLAR,
            balance=1000,
            user=user1,
        )
        Card.objects.create(
            number="8888999910101111",
            currency=Card.CURRENCY.RUBLE,
            balance=999,
            user=user2,
        )
        Card.objects.create(
            number="1212131314141515",
            currency=Card.CURRENCY.RUBLE,
            balance=1000,
            user=user3,
        )

    def test_check_transfer_is_exist(self):
        """Тест на проверку перевода денег: существует ли карта"""
        card = Card.objects.get(number="0000111122223333")
        card_transfer = Card.objects.get(number="8888999910101111")

        mess_exist, card_exist = TransferService().check_transfer_by_number(card, 500, "1111111111111111")
        mess, card1 = TransferService().check_transfer_by_number(card, 500, card_transfer.number)

        self.assertIsNone(card_exist)
        self.assertEquals(mess_exist, MESSAGE_EXIST_CARD)

        self.assertEquals(card1, card_transfer)
        self.assertEquals(mess, MESSAGE_CONFIRM)

    def test_check_transfer_summa(self):
        """Тест на проверку перевода денег: можно ли переводить такую сумму"""
        card = Card.objects.get(number="0000111122223333")
        card_transfer = Card.objects.get(number="8888999910101111")

        mess, card1 = TransferService().check_transfer_by_number(card, 500, card_transfer.number)
        mess_bad, card_bad = TransferService().check_transfer_by_number(card, 5000, card_transfer.number)
        mess_bad1, card_bad1 = TransferService().check_transfer_by_number(card, 0, card_transfer.number)
        mess_bad2, card_bad2 = TransferService().check_transfer_by_number(card, -5000, card_transfer.number)

        self.assertIsNone(card_bad)
        self.assertIsNone(card_bad1)
        self.assertIsNone(card_bad2)
        self.assertEquals(mess_bad, MESSAGE_NOT_ENOUGH_BALANCE)
        self.assertEquals(mess_bad1, MESSAGE_NOT_ENOUGH_BALANCE)
        self.assertEquals(mess_bad2, MESSAGE_NOT_ENOUGH_BALANCE)

        self.assertEquals(card1, card_transfer)
        self.assertEquals(mess, MESSAGE_CONFIRM)

    def test_check_transfer_myself(self):
        """Тест на проверку перевода денег: себе переводить нельзя"""
        card = Card.objects.get(number="0000111122223333")

        mess_bad, card_bad = TransferService().check_transfer_by_number(card, 500, card.number)

        self.assertIsNone(card_bad)
        self.assertEquals(mess_bad, MESSAGE_MYSELF_TRANSFER)

    def test_check_transfer_currency(self):
        """Тест на проверку перевода денег: валюты на обеих карт одинаковы"""
        card = Card.objects.get(number="8888999910101111")
        card_transfer = Card.objects.get(number="0000111122223333")

        mess_bad, card_bad = TransferService().check_transfer_by_number(card, 500, "4444555566667777")
        mess, card1 = TransferService().check_transfer_by_number(card, 500, card_transfer.number)

        self.assertIsNone(card_bad)
        self.assertEquals(mess_bad, MESSAGE_NOT_EQ_CURRENCY)

        self.assertEquals(card1, card_transfer)
        self.assertEquals(mess, MESSAGE_CONFIRM)

    def test_check_transfer_ban(self):
        """Тест на проверку перевода денег: нельзя переводить забаненому пользователю"""
        card = Card.objects.get(number="8888999910101111")
        card_transfer = Card.objects.get(number="1212131314141515")

        mess_bad, card_bad = TransferService().check_transfer_by_number(card, 500, card_transfer.number)

        self.assertIsNone(card_bad)
        self.assertEquals(mess_bad, MESSAGE_BAN_USER)

    def test_transfer(self):
        """Тест на перевод денег другому пользователю"""
        card, card_transfer, summa = TransferServiceTest.__get_test_data_for_transaction()

        self.assertEquals(card.balance, 0)
        self.assertEquals(card_transfer.balance, 1999)

    def test_transfer_transaction(self):
        """Тест на проверку перевода в другую валюту"""
        card, card_transfer, summa = TransferServiceTest.__get_test_data_for_transaction()

        transaction = UserTransactionHistory.objects.filter(card=card, card_transaction=card_transfer,
                                                            summa=summa,
                                                            type_transaction=BaseTransactionHistory.TYPE_TRANSACTION.USER)

        self.assertTrue(transaction.exists())

    def test_check_transfer_currency1(self):
        """Тест на перевод денег в другую валюту"""
        card1 = Card.objects.get(number="1212131314141515")
        card2 = Card.objects.get(number="8888999910101111")
        card3 = Card.objects.get(number="0000111122223333")

        self.assertFalse(TransferService().check_transfer_currency(card1.id, Card.CURRENCY.YUAN))
        self.assertFalse(TransferService().check_transfer_currency(card2.id, Card.CURRENCY.YUAN))
        self.assertFalse(TransferService().check_transfer_currency(card2.id, Card.CURRENCY.RUBLE))
        self.assertTrue(TransferService().check_transfer_currency(card3.id, Card.CURRENCY.YUAN))

    def test_transfer_currency(self):
        """Тест на перевод валюты"""
        card = Card.objects.get(number="0000111122223333")
        balance = card.balance
        currency = Card.CURRENCY.DOLLAR
        rates = ParseService().parse_course(card.currency)
        new_balance = balance / rates[currency]

        TransferService().transfer_currency(card.id, currency)
        card = Card.objects.get(number="0000111122223333")

        self.assertEquals(card.currency, Card.CURRENCY.DOLLAR)
        self.assertEquals(card.balance, new_balance)

        TransferService().transfer_currency(card.id, Card.CURRENCY.RUBLE)
        card = Card.objects.get(number="0000111122223333")
        self.assertEquals(round(card.balance), balance)
        self.assertEquals(card.currency, Card.CURRENCY.RUBLE)

    @staticmethod
    def __get_test_data_for_transaction():
        card = Card.objects.get(number="0000111122223333")
        card_transfer = Card.objects.get(number="8888999910101111")
        summa = 1000

        TransferService().transfer(card, card_transfer, summa)

        return card, card_transfer, summa


class ParseServiceTest(TestCase):
    def test_connection(self):
        re = requests.get(RATE_URL)
        self.assertEquals(re.status_code, HTTPStatus.OK)

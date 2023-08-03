from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from rolepermissions.roles import assign_role

from SberBank.roles import SimpleUser
from cards.models import Card
from chat.models import Room
from users.models import User


class CurrenciesViewTest(TestCase):
    def setUp(self):
        user1 = User.objects.create(first_name="Иван", last_name="Иванов", patronymic="Иванович",
                                    username="ivan@mail.ru")
        user1.set_password("1")
        user1.save()
        assign_role(user1, SimpleUser)
        Room.objects.create(user=user1)
        Card.objects.create(
            number="0000111122223333",
            currency=Card.CURRENCY.RUBLE,
            balance=1000,
            user=user1,
        )

    def test_view(self):
        self.client.login(username="ivan@mail.ru", password="1")
        card = Card.objects.get(number="0000111122223333")
        path = reverse("cards:my_card", kwargs={"card_id": card.id})
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "cards/my_card.html")

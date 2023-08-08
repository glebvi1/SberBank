import calendar
from datetime import date
from typing import Dict, Tuple

from rolepermissions.roles import assign_role

from SberBank.roles import VIPUser
from cards import MESSAGE_NOT_ENOUGH_BALANCE
from cards.models import Card
from history.models import UserTransactionHistory
from users.models import User
from vip_users import VIP_COST
from vip_users.models import Category


class VIPService:
    def buy_vip(self, user: User, card_id: int) -> Tuple[str, bool]:
        """Покупка VIP роли
        @param user: пользователь, который покупает VIP
        @param card_id: карта, которой пользователь расплачевается
        @return: Tuple[str, bool]
        """
        card = Card.objects.get(id=card_id)
        # TODO: TransferService().transfer(), создать админовскую карту

        if card.balance < VIP_COST:
            return MESSAGE_NOT_ENOUGH_BALANCE, False
        card.balance -= VIP_COST
        card.save()
        assign_role(user, VIPUser)
        return "", True

    def add_category_to_transaction(self, category_id: int, transaction_id: int) -> None:
        """Присваевает транзакции категорию
        @param category_id: id категории
        @param transaction_id: id транзакции
        @return: None
        """
        category = Category.objects.get(id=category_id)
        transaction = UserTransactionHistory.objects.get(id=transaction_id)

        transaction.category = category
        transaction.save()

    def check_new_category(self, user: User, category_name, not_edit_category_id):
        pred_category = Category.objects.get(id=not_edit_category_id)
        if pred_category.name == category_name:
            return True
        return not Category.objects.filter(user=user, name=category_name).exists()

    def delete_category(self, category_id):
        category = Category.objects.get(id=category_id)
        category.delete()


class StatisticsService:
    def get_statistics_for_category(self, user: User, category: Category, month: int, year: int) -> Dict[str, Dict[str, float]]:
        """Создает статистику для конкретной категории (доход-расход) за календарный месяц (01.month - last_day.month).
        Разные валюты учитываются.
        @param user: пользователь
        @param category: категория
        @param month: месяц (1..12)
        @param year: год
        @return: Dict[валюта1: Dict[расход/доход, общая сумма за месяц], ...]
        """
        statistic = {}
        for transaction in UserTransactionHistory.objects.filter(category=category,
                                                                 time__range=self.__get_month_range(month, year)):
            currency = transaction.currency
            if currency in statistic:
                if transaction.card.user == user:
                    statistic[currency]["-"] += transaction.summa
                else:
                    statistic[currency]["+"] += transaction.summa
            else:
                statistic[currency] = {}
                if transaction.card.user == user:
                    statistic[currency]["-"] = transaction.summa
                    statistic[currency]["+"] = 0
                else:
                    statistic[currency]["+"] = transaction.summa
                    statistic[currency]["-"] = 0
        return statistic

    def get_global_statistics_for_month(self, user: User, month: int, year: int) -> \
            Tuple[Dict[str, Dict[str, float]], Dict[str, Dict[str, float]]]:
        """Статистика для всех категорий за календарный месяц (01.month - last_day.month).
        @param user: пользователь, для его категорий создается статистика
        @param month: месяц (1..12)
        @param year: год
        @return: Два словаря: первый с доходами, второй с расходами. Вид:
        Dict[валюта1: Dict[категория1: сумма за месяц, категория2: сумма за месяц, ...], ...]
        """
        statistics_plus = {}
        statistics_neg = {}

        for category in Category.objects.filter(user=user):
            for transaction in UserTransactionHistory.objects.filter(category=category,
                                                                     time__range=self.__get_month_range(month, year)):
                currency = transaction.currency

                if transaction.card.user == user:
                    self.__add_category(statistics_neg, currency, category.name, transaction.summa)
                else:
                    self.__add_category(statistics_plus, currency, category.name, transaction.summa)

        return statistics_plus, statistics_neg

    def __add_category(self, statistics: dict, currency: str, name: str, summa: float):
        """Добавляет категорию к словарю statistics
        @param statistics: исходный словарь
        @param currency: валюта
        @param name: название категории
        @param summa: сумма
        @return:
        """
        if currency in statistics:
            if name in statistics[currency]:
                statistics[currency][name] += summa
            else:
                statistics[currency][name] = summa
        else:
            statistics[currency] = {name: summa}

    def __get_month_range(self, month: int, year: int) -> tuple[date, date]:
        """Создает две даты: начало и конец месяца
        @param month: месяц (1..12)
        @param year: год
        @return: tuple[date, date]
        """
        last_day = calendar.monthrange(year, month)[1]

        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        return start_date, end_date


def get_nearest_month_and_year(month, year):
    pred_month = month - 1 if month != 1 else 12
    next_month = month + 1 if month != 12 else 1

    pred_year = year - 1 if month == 1 else year
    next_year = year + 1 if month == 12 else year

    return pred_month, next_month, pred_year, next_year

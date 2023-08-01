import calendar
from datetime import date

from rolepermissions.roles import assign_role

from SberBank.roles import VIPUser
from cards import MESSAGE_NOT_ENOUGH_BALANCE
from cards.models import Card
from history.models import UserTransactionHistory
from vip_users import VIP_COST
from vip_users.models import Category


class VIPService:
    def buy_vip(self, user, card_id):
        card = Card.objects.get(id=card_id)
        # TODO: TransferService().transfer()

        if card.balance < VIP_COST:
            return MESSAGE_NOT_ENOUGH_BALANCE, False
        card.balance -= VIP_COST
        card.save()
        assign_role(user, VIPUser)
        return "", True

    def add_category_to_transaction(self, category_id, transaction_id):
        category = Category.objects.get(id=category_id)
        transaction = UserTransactionHistory.objects.get(id=transaction_id)

        transaction.category = category
        transaction.save()


class StatisticsService:
    def get_statistics_for_category(self, user, category, month):
        statistic = {}
        for transaction in UserTransactionHistory.objects.filter(category=category, time__range=self.__get_month_range(month)):
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

    def get_global_statistics_for_month(self, user, month):
        statistics_plus = {}
        statistics_neg = {}

        for category in Category.objects.filter(user=user):
            for transaction in UserTransactionHistory.objects.filter(category=category, time__range=self.__get_month_range(month)):
                currency = transaction.currency

                if transaction.card.user == user:
                    self.__add_category(statistics_neg, currency, category.name, transaction.summa)
                else:
                    self.__add_category(statistics_plus, currency, category.name, transaction.summa)

        return statistics_plus, statistics_neg

    def __add_category(self, statistics, currency, name, summa):
        if currency in statistics:
            if name in statistics[currency]:
                statistics[currency][name] += summa
            else:
                statistics[currency][name] = summa
        else:
            statistics[currency] = {name: summa}

    def __get_month_range(self, month):
        today = date.today().strftime("%d/%m/%Y").split("/")
        year = int(today[2])
        last_day = calendar.monthrange(year, month)[1]

        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        return start_date, end_date

import calendar
from datetime import date

from django.utils.timezone import now


class TransactionHistoryService:
    def get_all_sort_transaction(self, card):
        transactions = list(card.expense_transaction.all()) + list(card.income_transactions.all()) + list(card.currency_transactions.all())
        transactions = list(sorted(transactions, key=lambda history: history.time))[::-1]
        return transactions


class StatisticsService:
    def __get_transaction_for_currency(self, transactions):
        result = {}

        for transaction in transactions:
            if transaction.currency not in result:
                result[transaction.currency] = transaction.summa
            else:
                result[transaction.currency] += transaction.summa
        return result

    def create_month_period(self):
        today = date.today().strftime("%d/%m/%Y").split("/")
        year = int(today[2])
        month = int(today[1])
        last_day = calendar.monthrange(year, month)[1]

        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        return start_date, end_date

    def create_day_period(self):
        return now().date()

    def get_statistics(self, card):
        return self.__get_transaction_for_currency(card.income_transactions.filter(time__range=(self.create_month_period()))), \
               self.__get_transaction_for_currency(card.income_transactions.filter(time__date=self.create_day_period())),\
               self.__get_transaction_for_currency(card.expense_transaction.filter(time__range=(self.create_month_period()))),\
               self.__get_transaction_for_currency(card.expense_transaction.filter(time__date=self.create_day_period())),

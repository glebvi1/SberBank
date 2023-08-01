class TransactionHistoryService:
    def get_all_sort_transaction(self, card):
        transactions = list(card.expense_transaction.all()) + list(card.income_transactions.all()) + list(card.currency_transactions.all())
        transactions = list(sorted(transactions, key=lambda history: history.time))[::-1]
        return transactions

from celery import shared_task
from django.core.mail import send_mail

from SberBank.settings import EMAIL_HOST_USER


@shared_task
def send_email_to_user_income(fio, summa, currency_to_view, email):
    send_mail(
        "Поступление денег",
        f"Вам перевели {summa} {currency_to_view}."
        f"\nОт: {fio}",
        EMAIL_HOST_USER,
        [email]
    )


@shared_task
def send_email_to_user_expense(fio, summa, currency_to_view, email):
    send_mail(
        "Списание денег",
        f"Вы перевели {summa} {currency_to_view}."
        f"\nПолучатель: {fio}",
        EMAIL_HOST_USER,
        [email]
    )


@shared_task
def send_email_to_user_currency(summa, rate, currency_view, currency_after_transaction_view, email):
    send_mail(
        "Перевод валюты",
        f"Вы перевели {round(summa, 2)} {currency_view} = "
        f"{round(summa / rate, 2)} {currency_after_transaction_view}."
        f"\nПо курсу: 1 {currency_after_transaction_view} = {round(rate, 2)} {currency_view}",
        EMAIL_HOST_USER,
        [email]
    )


@shared_task
def send_email_to_user_add_card(number, email):
    send_mail(
        "Добавлена карта",
        f"Вам добавлена карта с номером: {number}",
        EMAIL_HOST_USER,
        [email]
    )
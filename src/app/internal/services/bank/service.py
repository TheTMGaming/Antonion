from typing import Union

from app.internal.models.bank import BankAccount, BankCard


def get_card(number: Union[int, str]) -> BankCard:
    return BankCard.objects.filter(number=number).first()


def get_bank_account(number: Union[int, str]) -> BankAccount:
    return BankAccount.objects.filter(number=number).first()

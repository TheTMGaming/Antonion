from typing import List

import pytest

from app.internal.models.bank import BankAccount
from app.internal.models.user import TelegramUser
from app.internal.services.bank.account import get_bank_account, get_bank_accounts


@pytest.mark.django_db
def test_getting_account_by_number(telegram_user: TelegramUser, bank_accounts: List[BankAccount]) -> None:
    actual = [get_bank_account(account.number) for account in bank_accounts]

    assert actual == list(BankAccount.objects.filter(owner=telegram_user))


@pytest.mark.django_db
def test_getting_accounts_by_user(telegram_user: TelegramUser, bank_accounts: List[BankAccount]) -> None:
    actual = list(get_bank_accounts(telegram_user))

    assert actual == list(BankAccount.objects.filter(owner=telegram_user))

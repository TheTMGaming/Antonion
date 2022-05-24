from typing import List

import pytest

from app.internal.bank.db.models import BankAccount
from app.internal.bank.db.repositories import BankAccountRepository, BankCardRepository
from app.internal.users.db.models import TelegramUser

account_repo = BankAccountRepository()


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_account_by_number(telegram_user: TelegramUser, bank_accounts: List[BankAccount]) -> None:
    actual = [account_repo.get_bank_account(account.number) for account in bank_accounts]

    assert actual == list(BankAccount.objects.filter(owner=telegram_user))


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_accounts_by_user(telegram_user: TelegramUser, bank_accounts: List[BankAccount]) -> None:
    actual = list(account_repo.get_bank_accounts(telegram_user))

    assert actual == list(BankAccount.objects.filter(owner=telegram_user))

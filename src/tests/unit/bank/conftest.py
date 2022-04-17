from typing import List

import pytest

from app.internal.models.bank import BankAccount, BankCard
from app.internal.models.user import TelegramUser


@pytest.fixture(scope="function")
def bank_accounts(telegram_user: TelegramUser, balance=10**4, amount=3) -> List[BankAccount]:
    return [BankAccount.objects.create(balance=balance, owner=telegram_user) for _ in range(amount)]


@pytest.fixture(scope="function")
def bank_account(bank_accounts: List[BankAccount]) -> BankAccount:
    return bank_accounts[0]


@pytest.fixture(scope="function")
def cards(bank_accounts: List[BankAccount]) -> List[BankCard]:
    return [BankCard.objects.create(bank_account=account) for account in bank_accounts]


@pytest.fixture(scope="function")
def card(cards: List[BankCard]) -> BankCard:
    return cards[0]

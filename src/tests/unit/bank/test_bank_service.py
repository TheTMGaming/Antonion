from typing import List

import pytest

from app.internal.models.bank import BankAccount, BankCard
from app.internal.models.user import TelegramUser
from app.internal.services.bank import get_documents


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_documents(
    telegram_user: TelegramUser, bank_accounts: List[BankAccount], cards: List[BankCard]
) -> None:
    actual_accounts, actual_cards = get_documents(telegram_user)

    assert sorted(actual_accounts, key=str) == sorted(bank_accounts, key=str)
    assert sorted(actual_cards, key=str) == sorted(cards, key=str)

from typing import List

import pytest

from app.internal.bank.db.models import BankCard
from app.internal.bank.db.repositories import BankCardRepository
from app.internal.users.db.models import TelegramUser

card_repo = BankCardRepository()


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_card_by_number(telegram_user: TelegramUser, cards: List[BankCard]) -> None:
    assert all(card_repo.get_card(card.number).bank_account.owner == telegram_user for card in cards)


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_cards_by_user(telegram_user: TelegramUser, cards: List[BankCard]) -> None:
    assert all(card.bank_account.owner == telegram_user for card in card_repo.get_cards(telegram_user))

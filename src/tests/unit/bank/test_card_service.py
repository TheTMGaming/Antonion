from typing import List

import pytest

from app.internal.models.bank import BankCard
from app.internal.models.user import TelegramUser
from app.internal.services.bank.card import get_card, get_cards


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_card_by_number(telegram_user: TelegramUser, cards: List[BankCard]) -> None:
    assert all(get_card(card.number).bank_account.owner == telegram_user for card in cards)


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_cards_by_user(telegram_user: TelegramUser, cards: List[BankCard]) -> None:
    assert all(card.bank_account.owner == telegram_user for card in get_cards(telegram_user))

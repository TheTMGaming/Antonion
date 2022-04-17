from typing import List

import pytest

from app.internal.models.bank import BankCard
from app.internal.models.user import TelegramUser
from app.internal.services.bank.card import get_card, get_cards


@pytest.mark.django_db
def test_getting_card_by_number(telegram_user: TelegramUser, cards: List[BankCard]) -> None:
    actual = [get_card(card.number) for card in cards]

    assert actual == list(BankCard.objects.filter(bank_account__owner=telegram_user))


@pytest.mark.django_db
def test_getting_cards_by_user(telegram_user: TelegramUser, cards: List[BankCard]) -> None:
    actual = get_cards(telegram_user)

    assert actual == list(BankCard.objects.filter(bank_account__owner=telegram_user))

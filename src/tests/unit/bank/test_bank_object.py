from typing import List

import pytest

from app.internal.bank.db.models import BankAccount, BankCard
from app.internal.bank.db.repositories import BankAccountRepository, BankCardRepository
from app.internal.bank.domain.services import BankObjectService
from app.internal.user.db.models import TelegramUser

bank_object_service = BankObjectService(account_repo=BankAccountRepository(), card_repo=BankCardRepository())


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_accounts_by_user(telegram_user: TelegramUser, bank_accounts: List[BankAccount]) -> None:
    actual = list(bank_object_service.get_bank_accounts(telegram_user))

    assert actual == list(BankAccount.objects.filter(owner=telegram_user))


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_cards_by_user(telegram_user: TelegramUser, cards: List[BankCard]) -> None:
    assert all(card.bank_account.owner == telegram_user for card in bank_object_service.get_cards(telegram_user))

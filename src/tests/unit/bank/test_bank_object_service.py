from typing import List

import pytest

from app.internal.bank.db.models import BankAccount, BankCard
from app.internal.general.services import bank_object_service
from app.internal.user.db.models import TelegramUser


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_bank_account_from_document(bank_account: BankAccount, card: BankCard) -> None:
    assert bank_account == bank_object_service.get_bank_account_from_document(bank_account)
    assert bank_account == bank_object_service.get_bank_account_from_document(card)


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_documents_order(
    telegram_user: TelegramUser, bank_accounts: List[BankAccount], cards: List[BankCard]
) -> None:
    order = bank_object_service.get_documents_order(telegram_user)

    assert sorted(order.keys()) == list(range(1, len(bank_accounts) + len(cards) + 1))
    assert sorted(order.values(), key=lambda obj: obj.number_field) == sorted(
        bank_accounts + cards, key=lambda obj: obj.number_field
    )


@pytest.mark.django_db
@pytest.mark.unit
def test_checking_balance_zero(bank_account: BankAccount, another_card: BankCard) -> None:
    assert bank_object_service.is_balance_zero(bank_account) is False
    assert bank_object_service.is_balance_zero(another_card) is False

    bank_account.balance = 0
    bank_account.save(update_fields=["balance"])

    another_card.bank_account.balance = 0
    another_card.bank_account.save(update_fields=["balance"])

    assert bank_object_service.is_balance_zero(bank_account) is True
    assert bank_object_service.is_balance_zero(another_card) is True


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_accounts_by_user(telegram_user: TelegramUser, bank_accounts: List[BankAccount]) -> None:
    actual = list(bank_object_service.get_bank_accounts(telegram_user))

    assert actual == list(BankAccount.objects.filter(owner=telegram_user))


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_account(telegram_user: TelegramUser, bank_account: BankAccount, another_account: BankAccount) -> None:
    assert bank_account == bank_object_service.get_bank_account(telegram_user, bank_account.number)
    assert bank_object_service.get_bank_account(telegram_user, another_account.number) is None


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_cards_by_user(telegram_user: TelegramUser, cards: List[BankCard]) -> None:
    assert all(card.bank_account.owner == telegram_user for card in bank_object_service.get_cards(telegram_user))


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_card(telegram_user: TelegramUser, card: BankCard, another_card: BankCard) -> None:
    assert card == bank_object_service.get_card(telegram_user, card.number)
    assert bank_object_service.get_card(telegram_user, another_card.number) is None


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_user_account_by_document_number(
    telegram_user: TelegramUser,
    bank_account: BankAccount,
    card: BankCard,
    another_account: BankAccount,
    another_card: BankCard,
) -> None:
    assert bank_account == bank_object_service.get_user_bank_account_by_document_number(
        telegram_user, bank_account.number
    )
    assert bank_account == bank_object_service.get_user_bank_account_by_document_number(telegram_user, card.number)
    assert bank_object_service.get_user_bank_account_by_document_number(telegram_user, another_account.number) is None
    assert bank_object_service.get_user_bank_account_by_document_number(telegram_user, another_card.number) is None


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_account_by_document_number(
    bank_account: BankAccount, card: BankCard, another_account: BankAccount, another_card: BankCard
) -> None:
    assert bank_account == bank_object_service.get_bank_account_by_document_number(bank_account.number)
    assert bank_account == bank_object_service.get_bank_account_by_document_number(card.number)
    assert another_account == bank_object_service.get_bank_account_by_document_number(another_account.number)
    assert another_account == bank_object_service.get_bank_account_by_document_number(another_card.number)

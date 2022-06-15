from typing import Callable, List

import freezegun
import pytest
from django.conf import settings
from django.db.models import Q
from django.http import HttpRequest
from django.utils import timezone
from ninja import UploadedFile

from app.internal.bank.db.models import BankAccount, BankCard, BankObject, Transaction
from app.internal.bank.domain.entities import BankAccountOut, BankCardOut, TransactionOut, TransferIn
from app.internal.bank.presentation.handlers import BankHandlers
from app.internal.general.rest.exceptions import BadRequestException, NotFoundException
from app.internal.general.services import bank_object_service, transaction_service, transfer_service
from tests.conftest import BALANCE

handlers = BankHandlers(bank_object_service, transaction_service, transfer_service)

NOW = timezone.now()


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_bank_accounts(http_request: HttpRequest, bank_accounts: List[BankAccount]) -> None:
    accounts = sorted(bank_accounts, key=lambda account: account.number)
    responses = sorted(handlers.get_bank_accounts(http_request), key=lambda account: account.number)

    assert len(responses) == len(accounts)
    for i in range(len(responses)):
        assert_bank_account_with_response(accounts[i], responses[i])


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_bank_account(http_request, bank_account: BankAccount) -> None:
    actual = handlers.get_bank_account(http_request, bank_account.number)

    assert_bank_account_with_response(bank_account, actual)


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_bank_account__invalid_number(
    http_request: HttpRequest, card: BankCard, bank_accounts: List[BankAccount]
) -> None:
    assert_getting_bank_object_in_handler(handlers.get_bank_account, http_request, bank_accounts, card)


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_account_history(
    http_request: HttpRequest, bank_account: BankAccount, another_accounts: List[BankAccount]
) -> None:
    transactions = sorted(
        Transaction.objects.bulk_create(
            Transaction(source=bank_account, destination=account) for account in another_accounts
        ),
        key=lambda transaction: transaction.created_at,
    )
    responses = sorted(
        handlers.get_account_history(http_request, bank_account.number), key=lambda transaction: transaction.created_at
    )

    assert len(responses) == len(transactions)
    for i in range(len(responses)):
        assert_transaction_with_response(transactions[i], responses[i])


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_account_history__invalid_number(
    http_request: HttpRequest, bank_accounts: List[BankAccount], card: BankCard
) -> None:
    assert_getting_bank_object_in_handler(handlers.get_account_history, http_request, bank_accounts, card)


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_cards(http_request: HttpRequest, cards: List[BankCard]) -> None:
    cards = sorted(cards, key=lambda card: card.number)
    responses = sorted(handlers.get_bank_cards(http_request), key=lambda card: card.number)

    assert len(responses) == len(cards)
    for i in range(len(responses)):
        assert_card_with_response(cards[i], responses[i])


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_card(http_request: HttpRequest, card: BankCard) -> None:
    response = handlers.get_bank_card(http_request, card.number)

    assert_card_with_response(card, response)


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_card__invalid_number(
    http_request: HttpRequest, cards: List[BankCard], bank_account: BankAccount
) -> None:
    assert_getting_bank_object_in_handler(handlers.get_bank_card, http_request, cards, bank_account)


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_card_history(http_request: HttpRequest, card: BankCard, another_cards: List[BankCard]) -> None:
    transactions = sorted(
        Transaction.objects.bulk_create(
            Transaction(source=card.bank_account, destination=another.bank_account) for another in another_cards
        ),
        key=lambda transaction: transaction.created_at,
    )
    responses = sorted(
        handlers.get_card_history(http_request, card.number), key=lambda transaction: transaction.created_at
    )

    assert len(responses) == len(transactions)
    for i in range(len(responses)):
        assert_transaction_with_response(transactions[i], responses[i])


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_card_history__invalid_number(
    http_request: HttpRequest, cards: List[BankCard], bank_account: BankAccount
) -> None:
    assert_getting_bank_object_in_handler(handlers.get_card_history, http_request, cards, bank_account)


@pytest.mark.django_db
@pytest.mark.integration
@freezegun.freeze_time(NOW)
def test_transfer_account_to_account(
    http_request, bank_account: BankAccount, another_account: BankAccount, uploaded_image: UploadedFile
) -> None:
    assert_transfer_bank_objects(http_request, bank_account, another_account)
    assert_transfer_bank_objects(http_request, bank_account, another_account, uploaded_image)


@pytest.mark.django_db
@pytest.mark.integration
@freezegun.freeze_time(NOW)
def test_transfer_account_to_card(
    http_request, bank_account: BankAccount, another_card: BankCard, uploaded_image: UploadedFile
) -> None:
    assert_transfer_bank_objects(http_request, bank_account, another_card)
    assert_transfer_bank_objects(http_request, bank_account, another_card, uploaded_image)


@pytest.mark.django_db
@pytest.mark.integration
@freezegun.freeze_time(NOW)
def test_transfer_card_to_account(
    http_request, card: BankCard, another_account: BankAccount, uploaded_image: UploadedFile
) -> None:
    assert_transfer_bank_objects(http_request, card, another_account)
    assert_transfer_bank_objects(http_request, card, another_account, uploaded_image)


@pytest.mark.django_db
@pytest.mark.integration
@freezegun.freeze_time(NOW)
def test_transfer_card_to_card(
    http_request, card: BankCard, another_card: BankCard, uploaded_image: UploadedFile
) -> None:
    assert_transfer_bank_objects(http_request, card, another_card)
    assert_transfer_bank_objects(http_request, card, another_card, uploaded_image)


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize("accrual", [-10, -0.0000001, -0.01, 0])
def test_transfer__invalid_accrual(http_request: HttpRequest, accrual: float) -> None:
    with pytest.raises(BadRequestException):
        handlers.transfer(http_request, TransferIn(source=0, destination=0, accrual=accrual))


@pytest.mark.django_db
@pytest.mark.integration
def test_transfer__not_found_source(
    http_request: HttpRequest, another_card: BankCard, another_account: BankAccount
) -> None:
    with pytest.raises(NotFoundException):
        handlers.transfer(http_request, TransferIn(source=another_card.number, destination=0, accrual=1), None)
        handlers.transfer(http_request, TransferIn(source=another_account.number, destination=0, accrual=1), None)


@pytest.mark.django_db
@pytest.mark.integration
def test_transfer__not_found_destination(http_request: HttpRequest, card: BankCard, bank_account: BankAccount) -> None:
    with pytest.raises(NotFoundException):
        handlers.transfer(http_request, TransferIn(source=card.number, destination=0, accrual=1), None)
        handlers.transfer(http_request, TransferIn(source=bank_account.number, destination=0, accrual=1), None)


@pytest.mark.django_db
@pytest.mark.integration
def test_transfer__source_equals_destination(
    http_request: HttpRequest, card: BankCard, bank_account: BankAccount
) -> None:
    with pytest.raises(BadRequestException):
        handlers.transfer(
            http_request, TransferIn(source=bank_account.number, destination=card.number, accrual=1), None
        )
        handlers.transfer(
            http_request, TransferIn(source=bank_account.number, destination=bank_account.number, accrual=1), None
        )


@pytest.mark.django_db
@pytest.mark.integration
def test_transfer__invalid_file(
    http_request: HttpRequest, bank_account: BankAccount, another_account: BankAccount, uploaded_image: UploadedFile
) -> None:
    transfer_in = TransferIn(source=bank_account.number, destination=another_account.number, accrual=1)
    with pytest.raises(BadRequestException):
        for size in [
            settings.MAX_SIZE_PHOTO_BYTES + 1,
            settings.MAX_SIZE_PHOTO_BYTES + 10**-2,
            settings.MAX_SIZE_PHOTO_BYTES + 10**-5,
        ]:
            uploaded_image.size = size
            handlers.transfer(http_request, transfer_in, uploaded_image)

        uploaded_image.size = settings.MAX_SIZE_PHOTO_BYTES
        uploaded_image.content_type = "text/plain"
        handlers.transfer(http_request, transfer_in, uploaded_image)


def assert_transfer_bank_objects(
    http_request: HttpRequest, source: BankObject, destination: BankObject, photo: UploadedFile = None
) -> None:
    eps = 10**-12
    accrual = 10
    body = TransferIn(source=source.number_field, destination=destination.number_field, accrual=accrual)

    source.refresh_from_db()
    destination.refresh_from_db()
    Transaction.objects.all().delete()
    prev_source_balance, prev_destination_balance = source.get_balance(), destination.get_balance()

    transaction_out = handlers.transfer(http_request, body, photo)

    actual_source = BankAccount.objects.filter(
        Q(number=source.number_field) | Q(bank_cards__number=source.number_field)
    ).first()
    actual_destination = BankAccount.objects.filter(
        Q(number=destination.number_field) | Q(bank_cards__number=destination.number_field)
    ).first()

    transaction = Transaction.objects.filter(source=actual_source, destination=actual_destination).first()

    assert actual_source.number == transaction_out.source
    assert actual_destination.number == transaction_out.destination
    assert abs(accrual - transaction_out.accrual) < eps
    assert NOW == transaction_out.created_at
    assert abs(prev_source_balance - accrual - actual_source.balance) < eps
    assert abs(prev_destination_balance + accrual - actual_destination.balance) < eps
    assert transaction is not None
    if photo is not None:
        url = transaction.photo.url
        transaction.photo.delete(save=False)

        assert transaction_out.photo == url


def assert_bank_account_with_response(account: BankAccount, response: BankAccountOut) -> None:
    assert account.number == response.number
    assert account.balance == response.balance


def assert_card_with_response(card: BankCard, response: BankCardOut) -> None:
    assert str(card.number) == response.number
    assert_bank_account_with_response(card.bank_account, response.account)


def assert_transaction_with_response(transaction: Transaction, response: TransactionOut) -> None:
    assert str(transaction.source.number) == response.source
    assert str(transaction.destination.number) == response.destination
    assert abs(transaction.accrual.__float__() - response.accrual) < 10**-9
    assert transaction.created_at == response.created_at
    assert (transaction.photo.url if transaction.photo else None) == response.photo


def assert_getting_bank_object_in_handler(
    handler: Callable, http_request: HttpRequest, objects: List[BankObject], another_type_object: BankObject
) -> None:
    min_number = min(obj.number_field for obj in objects)
    max_number = max(obj.number_field for obj in objects)

    with pytest.raises(NotFoundException):
        handler(http_request, -1)
        handler(http_request, 10)
        handler(http_request, min_number - 1)
        handler(http_request, max_number + 1)
        handler(http_request, another_type_object.number_field)

from decimal import Decimal
from typing import List

from django.http import HttpRequest
from ninja import Body

from app.internal.bank.db.models import BankAccount, BankCard, Transaction
from app.internal.bank.domain.entities import BankAccountOut, BankCardOut, TransactionOut, TransferIn
from app.internal.bank.domain.services import BankObjectService, TransactionService, TransferService
from app.internal.general.exceptions import BadRequestException, IntegrityException, NotFoundException
from app.internal.user.db.models import TelegramUser


class BankHandlers:
    def __init__(
        self,
        bank_obj_service: BankObjectService,
        transaction_service: TransactionService,
        transfer_service: TransferService,
    ):
        self._bank_obj_service = bank_obj_service
        self._transaction_service = transaction_service
        self._transfer_service = transfer_service

    def get_bank_accounts(self, request: HttpRequest) -> List[BankAccountOut]:
        accounts = self._bank_obj_service.get_bank_accounts(request.telegram_user)

        return [BankAccountOut.from_orm(account) for account in accounts]

    def get_bank_account(self, request: HttpRequest, number: int) -> BankAccountOut:
        account = self._try_get_account(request.telegram_user, number)

        return BankAccountOut.from_orm(account)

    def get_account_history(self, request: HttpRequest, number: int) -> List[TransactionOut]:
        account = self._try_get_account(request.telegram_user, number)

        return self._create_history_response(account)

    def get_bank_cards(self, request: HttpRequest) -> List[BankCardOut]:
        cards = self._bank_obj_service.get_cards(request.telegram_user)

        return [self._get_card_response(card) for card in cards]

    def get_bank_card(self, request: HttpRequest, number: int) -> BankCardOut:
        card = self._try_get_card(request.telegram_user, number)

        return self._get_card_response(card)

    def get_card_history(self, request: HttpRequest, number: int) -> List[TransactionOut]:
        card = self._try_get_card(request.telegram_user, number)
        account = self._bank_obj_service.get_bank_account_from_document(card)

        return self._create_history_response(account)

    def transfer(self, request: HttpRequest, transfer: TransferIn = Body(...)) -> TransactionOut:
        accrual = Decimal(transfer.accrual)

        if not self._transfer_service.validate_accrual(accrual):
            raise BadRequestException("Invalid accrual")

        source = self._bank_obj_service.get_user_bank_account_by_document_number(request.telegram_user, transfer.source)
        if not source:
            raise NotFoundException("source")

        destination = self._bank_obj_service.get_bank_account_by_document_number(transfer.destination)
        if not destination:
            raise NotFoundException("destination")

        if source == destination:
            raise BadRequestException("Source account equals destination account")

        transaction = self._transfer_service.try_transfer(source, destination, accrual)
        if not transaction:
            raise IntegrityException()

        return self._get_transaction_response(transaction)

    def _try_get_account(self, user: TelegramUser, number: int) -> BankAccount:
        account = self._bank_obj_service.get_bank_account(user, number)

        if not account:
            raise NotFoundException("account")

        return account

    def _try_get_card(self, user: TelegramUser, number: int) -> BankCard:
        card = self._bank_obj_service.get_card(user, number)

        if not card:
            raise NotFoundException("card")

        return card

    def _create_history_response(self, account: BankAccount) -> List[TransactionOut]:
        transactions = self._transaction_service.get_transactions(account)

        return [self._get_transaction_response(transaction) for transaction in transactions]

    def _get_transaction_response(self, transaction: Transaction) -> TransactionOut:
        return TransactionOut(
            source=transaction.source.number,
            destination=transaction.destination.number,
            accrual=transaction.accrual,
            created_at=transaction.created_at,
        )

    def _get_card_response(self, card: BankCard) -> BankCardOut:
        return BankCardOut(number=card.number, account=BankAccountOut.from_orm(card.bank_account))

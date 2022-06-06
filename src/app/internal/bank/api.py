from ninja import NinjaAPI

from app.internal.bank.db.repositories import BankAccountRepository, BankCardRepository, TransactionRepository
from app.internal.bank.domain.services import BankObjectService, TransactionService, TransferService
from app.internal.bank.presentation.handlers import BankHandlers
from app.internal.bank.presentation.routers import get_bank_router


def register_bank_api(api: NinjaAPI) -> None:
    account_repo = BankAccountRepository()
    card_repo = BankCardRepository()
    transaction_repo = TransactionRepository()

    bank_obj_service = BankObjectService(account_repo, card_repo)
    transaction_service = TransactionService(transaction_repo)
    transfer_service = TransferService(account_repo, card_repo, transaction_repo)

    bank_handlers = BankHandlers(bank_obj_service, transaction_service, transfer_service)

    api.add_router(prefix="/bank", router=get_bank_router(bank_handlers))

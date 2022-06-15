from ninja import NinjaAPI

from app.internal.bank.presentation.handlers import BankHandlers
from app.internal.bank.presentation.routers import get_bank_router
from app.internal.general.services import bank_object_service, transaction_service, transfer_service


def register_bank_api(api: NinjaAPI) -> None:
    bank_handlers = BankHandlers(bank_object_service, transaction_service, transfer_service)

    api.add_router(prefix="/bank", router=get_bank_router(bank_handlers))

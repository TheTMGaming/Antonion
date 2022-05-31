from typing import List

from ninja import Router

from app.internal.authentication.presentation import JWTAuthentication
from app.internal.bank.domain.entities import BankAccountOut, BankCardOut, TransactionOut
from app.internal.bank.presentation.handlers import BankHandlers
from app.internal.general.responses import ErrorResponse


def get_bank_router(bank_handlers: BankHandlers) -> Router:
    router = Router(tags=["bank"], auth=[JWTAuthentication()])

    router.add_api_operation(
        path="/accounts",
        methods=["GET"],
        view_func=bank_handlers.get_bank_accounts,
        response={200: List[BankAccountOut]},
    )

    router.add_api_operation(
        path="/accounts/{int:number}",
        methods=["GET"],
        view_func=bank_handlers.get_bank_account,
        response={200: BankAccountOut, 404: ErrorResponse},
    )

    router.add_api_operation(
        path="/accounts/{int:number}/history",
        methods=["GET"],
        view_func=bank_handlers.get_account_history,
        response={200: List[TransactionOut], 404: ErrorResponse},
    )

    router.add_api_operation(
        path="/cards", methods=["GET"], view_func=bank_handlers.get_bank_cards, response={200: List[BankCardOut]}
    )

    router.add_api_operation(
        path="/cards/{int:number}",
        methods=["GET"],
        view_func=bank_handlers.get_bank_card,
        response={200: BankCardOut, 404: ErrorResponse},
    )

    router.add_api_operation(
        path="/cards/{int:number}/history",
        methods=["GET"],
        view_func=bank_handlers.get_card_history,
        response={200: List[TransactionOut], 404: ErrorResponse},
    )

    router.add_api_operation(
        path="/transfer",
        methods=["POST"],
        view_func=bank_handlers.transfer,
        response={200: TransactionOut, 400: ErrorResponse},
    )

    return router

from ninja import Router

from app.internal.authentication.presentation import JWTAuthentication
from app.internal.general.responses import SuccessResponse, ErrorResponse
from app.internal.user.domain.entities.user import TelegramUserOut, PhoneSchema
from app.internal.user.presentation.handlers import TelegramUserHandlers


def get_user_router(user_handlers: TelegramUserHandlers) -> Router:
    router = Router(tags=["user"], auth=[JWTAuthentication()])

    router.add_api_operation(
        path="/me",
        methods=["GET"],
        view_func=user_handlers.get_about_me,
        response={200: TelegramUserOut}
    )

    router.add_api_operation(
        path="/phone",
        methods=["PATCH"],
        view_func=user_handlers.update_phone,
        response={200: PhoneSchema, 400: ErrorResponse}
    )

    router.add_api_operation(
        path="/password",
        methods=["PATCH"],
        view_func=user_handlers.update_password,
        response={200: SuccessResponse, 500: ErrorResponse}
    )

    return router

from ninja import Router

from app.internal.authentication.presentation import JWTAuthentication
from app.internal.user.presentation.handlers import TelegramUserHandlers


def get_user_router(user_handlers: TelegramUserHandlers) -> Router:
    router = Router(tags=["user"], auth=[JWTAuthentication()])

    router.add_api_operation(path="/me/", methods=["GET"], view_func=user_handlers.get_about_me)

    router.add_api_operation(path="/me/", methods=["PUT"], view_func=user_handlers.update_me)

    router.add_api_operation(path="/phone/", methods=["PATCH"], view_func=user_handlers.update_phone)

    router.add_api_operation(path="/password/", methods=["PATCH"], view_func=user_handlers.update_password)

    return router

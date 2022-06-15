from ninja import NinjaAPI

from app.internal.general.services import friend_service, request_service, user_service
from app.internal.user.presentation.handlers import FriendHandlers, TelegramUserHandlers
from app.internal.user.presentation.routers import get_friends_router, get_user_router


def register_user_api(api: NinjaAPI) -> None:
    user_handlers = TelegramUserHandlers(user_service)

    api.add_router(prefix="/user", router=get_user_router(user_handlers))


def register_friends_api(api: NinjaAPI) -> None:
    friend_handlers = FriendHandlers(user_service, friend_service, request_service)

    api.add_router(prefix="/friends", router=get_friends_router(friend_handlers))

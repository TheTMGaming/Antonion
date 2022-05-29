from ninja import NinjaAPI

from app.internal.user.db.repositories import SecretKeyRepository, TelegramUserRepository, FriendRequestRepository
from app.internal.user.domain.services import TelegramUserService, FriendService, FriendRequestService
from app.internal.user.presentation.handlers import TelegramUserHandlers, FriendHandlers
from app.internal.user.presentation.routers import get_user_router, get_friends_router


def add_user_api(api: NinjaAPI) -> None:
    user_service = TelegramUserService(user_repo=TelegramUserRepository(), secret_key_repo=SecretKeyRepository())
    user_handlers = TelegramUserHandlers(user_service=user_service)

    api.add_router(prefix="", router=get_user_router(user_handlers))


def add_friend_api(api: NinjaAPI) -> None:
    user_service = TelegramUserService(user_repo=TelegramUserRepository(), secret_key_repo=SecretKeyRepository())
    friend_service = FriendService(friend_repo=TelegramUserRepository())
    request_service = FriendRequestService(request_repo=FriendRequestRepository())

    friend_handlers = FriendHandlers(user_service=user_service, friend_service=friend_service, request_service=request_service)

    api.add_router(prefix="/friends", router=get_friends_router(friend_handlers))

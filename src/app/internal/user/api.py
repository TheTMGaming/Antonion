from ninja import NinjaAPI

from app.internal.user.db.repositories import FriendRequestRepository, SecretKeyRepository, TelegramUserRepository
from app.internal.user.domain.services import FriendRequestService, FriendService, TelegramUserService
from app.internal.user.presentation.handlers import FriendHandlers, TelegramUserHandlers
from app.internal.user.presentation.routers import get_friends_router, get_user_router


def register_user_api(api: NinjaAPI) -> None:
    user_repo = TelegramUserRepository()
    secret_repo = SecretKeyRepository()

    user_service = TelegramUserService(user_repo, secret_repo)

    user_handlers = TelegramUserHandlers(user_service)

    api.add_router(prefix="/user", router=get_user_router(user_handlers))


def register_friends_api(api: NinjaAPI) -> None:
    user_repo = TelegramUserRepository()
    secret_repo = SecretKeyRepository()
    request_repo = FriendRequestRepository()

    user_service = TelegramUserService(user_repo, secret_repo)
    friend_service = FriendService(friend_repo=user_repo)
    request_service = FriendRequestService(request_repo)

    friend_handlers = FriendHandlers(user_service, friend_service, request_service)

    api.add_router(prefix="/friends", router=get_friends_router(friend_handlers))

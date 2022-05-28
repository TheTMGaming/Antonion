from ninja import NinjaAPI

from app.internal.user.db.repositories import SecretKeyRepository, TelegramUserRepository
from app.internal.user.domain.services import TelegramUserService
from app.internal.user.presentation.handlers import TelegramUserHandlers
from app.internal.user.presentation.routers import get_user_router


def add_user_api(api: NinjaAPI) -> None:
    user_service = TelegramUserService(user_repo=TelegramUserRepository(), secret_key_repo=SecretKeyRepository())
    user_handlers = TelegramUserHandlers(user_service=user_service)

    api.add_router(prefix="/user", router=get_user_router(user_handlers))

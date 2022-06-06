from ninja import NinjaAPI

from app.internal.authentication.db.repositories import AuthRepository
from app.internal.authentication.domain.services import JWTService
from app.internal.authentication.presentation.handlers import AuthHandlers
from app.internal.authentication.presentation.routers import get_auth_router
from app.internal.user.db.repositories import TelegramUserRepository


def register_auth_api(api: NinjaAPI) -> None:
    auth_repo = AuthRepository()
    user_repo = TelegramUserRepository()

    auth_service = JWTService(auth_repo, user_repo)

    auth_handlers = AuthHandlers(auth_service)

    api.add_router("/auth", get_auth_router(auth_handlers))

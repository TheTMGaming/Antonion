from ninja import NinjaAPI

from app.internal.authentication.db.repositories import AuthRepository
from app.internal.authentication.domain.services import JWTService
from app.internal.authentication.presentation.handlers import AuthHandlers
from app.internal.authentication.presentation.routers import get_auth_router
from app.internal.user.db.repositories import TelegramUserRepository


def add_auth_api(api: NinjaAPI) -> None:
    service = JWTService(auth_repo=AuthRepository(), user_repo=TelegramUserRepository())
    auth_handlers = AuthHandlers(auth_service=service)

    router = get_auth_router(auth_handlers)
    api.add_router("/auth", router)

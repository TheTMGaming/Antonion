from ninja import NinjaAPI

from app.internal.authentication.presentation.handlers import AuthHandlers
from app.internal.authentication.presentation.routers import get_auth_router
from app.internal.general.services import auth_service


def register_auth_api(api: NinjaAPI) -> None:
    auth_handlers = AuthHandlers(auth_service)

    api.add_router("/auth", get_auth_router(auth_handlers))

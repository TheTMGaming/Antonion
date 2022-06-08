from ninja import Router

from app.internal.authentication.domain.entities import AccessTokenOut
from app.internal.authentication.presentation.handlers import AuthHandlers
from app.internal.general.rest.responses import ErrorResponse


def get_auth_router(auth_handlers: AuthHandlers) -> Router:
    router = Router(tags=["auth"])

    router.add_api_operation(
        path="/login",
        methods=["POST"],
        view_func=auth_handlers.login,
        response={200: AccessTokenOut, 401: ErrorResponse},
    )

    router.add_api_operation(
        path="/refresh",
        methods=["POST"],
        view_func=auth_handlers.refresh,
        response={200: AccessTokenOut, 401: ErrorResponse, 400: ErrorResponse},
    )

    return router

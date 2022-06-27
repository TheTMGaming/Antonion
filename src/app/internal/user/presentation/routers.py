from typing import List

from ninja import Router

from app.internal.authentication.presentation import JWTAuthentication
from app.internal.general.rest.responses import ErrorResponse, SuccessResponse
from app.internal.user.domain.entities.friends import FriendRequestOut
from app.internal.user.domain.entities.user import PhoneIn, TelegramUserOut
from app.internal.user.presentation.handlers import FriendHandlers, TelegramUserHandlers


def get_user_router(user_handlers: TelegramUserHandlers) -> Router:
    router = Router(tags=["user"], auth=[JWTAuthentication()])

    router.add_api_operation(
        path="/me",
        methods=["GET"],
        view_func=user_handlers.get_about_me,
        response={200: TelegramUserOut},
        url_name="me",
    )

    router.add_api_operation(
        path="/phone",
        methods=["PATCH"],
        view_func=user_handlers.update_phone,
        response={200: PhoneIn, 400: ErrorResponse},
    )

    router.add_api_operation(
        path="/password",
        methods=["PATCH"],
        view_func=user_handlers.update_password,
        response={200: SuccessResponse},
    )

    return router


def get_friends_router(friend_handlers: FriendHandlers) -> Router:
    router = Router(tags=["friends"], auth=[JWTAuthentication()])

    router.add_api_operation(
        path="", methods=["GET"], view_func=friend_handlers.get_friends, response={200: List[TelegramUserOut]}
    )

    router.add_api_operation(
        path="/requests",
        methods=["GET"],
        view_func=friend_handlers.get_friend_requests,
        response={200: List[FriendRequestOut]},
    )

    router.add_api_operation(
        path="/{str:identifier}",
        methods=["GET"],
        view_func=friend_handlers.get_friend,
        response={200: TelegramUserOut, 404: ErrorResponse},
    )

    router.add_api_operation(
        path="/{str:identifier}",
        methods=["POST"],
        view_func=friend_handlers.add_friend,
        response={200: SuccessResponse, 404: ErrorResponse, 400: ErrorResponse},
    )

    router.add_api_operation(
        path="/{str:identifier}/accept",
        methods=["POST"],
        view_func=friend_handlers.accept_friend_request,
        response={200: SuccessResponse, 404: ErrorResponse},
    )

    router.add_api_operation(
        path="/{str:identifier}/reject",
        methods=["POST"],
        view_func=friend_handlers.reject_friend_request,
        response={200: SuccessResponse, 404: ErrorResponse},
    )

    router.add_api_operation(
        path="/{str:identifier}",
        methods=["DELETE"],
        view_func=friend_handlers.remove_friend,
        response={200: SuccessResponse, 404: ErrorResponse},
    )

    return router

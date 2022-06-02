from typing import List

from django.http import HttpRequest

from app.internal.general.exceptions import BadRequestException, NotFoundException
from app.internal.general.responses import SuccessResponse
from app.internal.user.db.models import TelegramUser
from app.internal.user.domain.entities.friends import FriendRequestOut
from app.internal.user.domain.entities.user import TelegramUserOut
from app.internal.user.domain.services import FriendRequestService, FriendService, TelegramUserService


class FriendHandlers:
    def __init__(
        self, user_service: TelegramUserService, friend_service: FriendService, request_service: FriendRequestService
    ):
        self._user_service = user_service
        self._friend_service = friend_service
        self._request_service = request_service

    def get_friends(self, request: HttpRequest) -> List[TelegramUserOut]:
        friends = self._friend_service.get_friends(request.telegram_user)

        return [TelegramUserOut.from_orm(friend) for friend in friends]

    def get_friend(self, request: HttpRequest, identifier: str) -> TelegramUserOut:
        friend = self._try_get_friend(request, identifier)

        return TelegramUserOut.from_orm(friend)

    def remove_friend(self, request: HttpRequest, identifier: str) -> SuccessResponse:
        friend = self._try_get_friend(request, identifier)

        self._friend_service.try_remove_from_friends(request.telegram_user, friend)

        return SuccessResponse()

    def add_friend(self, request: HttpRequest, identifier: str) -> SuccessResponse:
        user = self._try_get_user(identifier)

        if self._friend_service.is_friend_exists(request.telegram_user, user):
            raise BadRequestException("User is already friend")

        if not self._request_service.create(request.telegram_user, user):
            raise BadRequestException("Friend request already exists")

        return SuccessResponse()

    def get_friend_requests(self, request: HttpRequest) -> List[FriendRequestOut]:
        usernames = self._request_service.get_usernames_to_friends(request.telegram_user)

        return [FriendRequestOut(username=username) for username in usernames]

    def accept_friend_request(self, request: HttpRequest, identifier: str) -> SuccessResponse:
        user = self._try_get_user(identifier)

        if not self._request_service.try_accept(user, request.telegram_user):
            raise BadRequestException("Friend request does not exist")

        return SuccessResponse()

    def reject_friend_request(self, request: HttpRequest, identifier: str) -> SuccessResponse:
        user = self._try_get_user(identifier)

        if not self._request_service.try_reject(user, request.telegram_user):
            raise BadRequestException("Friend request does not exist")

        return SuccessResponse()

    def _try_get_user(self, identifier: str) -> TelegramUser:
        user = self._user_service.get_user(identifier)

        if not user:
            raise NotFoundException("user")

        return user

    def _try_get_friend(self, request: HttpRequest, identifier: str) -> TelegramUser:
        friend = self._friend_service.get_friend(request.telegram_user, identifier)

        if not friend:
            raise NotFoundException("friend")

        return friend

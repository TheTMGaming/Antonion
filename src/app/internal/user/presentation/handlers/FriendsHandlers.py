from django.http import HttpRequest

from app.internal.user.domain.services import FriendService, TelegramUserService


class FriendsHandlers:
    def __init__(self, user_service: TelegramUserService, friend_service: FriendService):
        self._user_service = user_service
        self._friend_service = friend_service

    def get_friends(self, request: HttpRequest):
        pass

    def remove_friend(self, request: HttpRequest):
        pass

    def create_friend_request(self, request: HttpRequest):
        pass

    def get_friend_requests(self, request: HttpRequest):
        pass

    def accept_friend_request(self, request: HttpRequest):
        pass

    def reject_friend_request(self, request: HttpRequest):
        pass

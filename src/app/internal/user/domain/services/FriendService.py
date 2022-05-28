from typing import Dict, Union

from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from telegram import User

from app.internal.user.db.models import TelegramUser
from app.internal.user.domain.interfaces import IFriendRepository, IFriendRequestRepository


class FriendService:
    def __init__(self, friend_repo: IFriendRepository, request_repo: IFriendRequestRepository):
        self._friend_repo = friend_repo
        self._request_repo = request_repo

    def get_friend(self, user: TelegramUser, friend_identifier: Union[int, str]):
        return self._friend_repo.get_friend(user.id, friend_identifier)

    def get_friends(self, user: TelegramUser) -> QuerySet[TelegramUser]:
        return self._friend_repo.get_friends(user.id)

    def get_friends_as_dict(self, user: TelegramUser) -> Dict[int, TelegramUser]:
        return dict((num, friend) for num, friend in enumerate(self._friend_repo.get_friends(user.id), 1))

    def try_create_friend_request(self, source: TelegramUser, destination: TelegramUser) -> bool:
        if self._request_repo.exists(source, destination):
            return False

        self._request_repo.create(source, destination)

        return True

    def reject_friend_request(self, source: TelegramUser, destination: TelegramUser) -> None:
        self._request_repo.remove(source, destination)

    def try_accept_friend(self, source: TelegramUser, destination: TelegramUser) -> bool:
        request = self._request_repo.get(source, destination)

        if not request:
            return False

        try:
            with transaction.atomic():
                source.friends.add(destination)
                request.delete()
        except IntegrityError:
            return False

        return True

    def try_remove_from_friends(self, first: TelegramUser, second: TelegramUser) -> bool:
        try:
            with transaction.atomic():
                first.friends.remove(second)
            return True
        except IntegrityError:
            return False

    def is_friend_exists(self, user: TelegramUser, friend: TelegramUser) -> bool:
        return self._friend_repo.is_friend_exists(user.id, friend.id)

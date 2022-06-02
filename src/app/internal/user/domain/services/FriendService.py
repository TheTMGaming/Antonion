from typing import Dict, Union

from django.db.models import QuerySet

from app.internal.user.db.models import TelegramUser
from app.internal.user.domain.interfaces import IFriendRepository


class FriendService:
    def __init__(self, friend_repo: IFriendRepository):
        self._friend_repo = friend_repo

    def get_friend(self, user: TelegramUser, friend_identifier: Union[int, str]):
        return self._friend_repo.get_friend(user.id, friend_identifier)

    def get_friends(self, user: TelegramUser) -> QuerySet[TelegramUser]:
        return self._friend_repo.get_friends(user.id)

    def get_friends_as_dict(self, user: TelegramUser) -> Dict[int, TelegramUser]:
        return dict((num, friend) for num, friend in enumerate(self._friend_repo.get_friends(user.id), 1))

    def remove_from_friends(self, source: TelegramUser, friend: TelegramUser) -> None:
        self._friend_repo.remove(source, friend)

    def is_friend_exists(self, user: TelegramUser, friend: TelegramUser) -> bool:
        return self._friend_repo.is_friend_exists(user.id, friend.id)

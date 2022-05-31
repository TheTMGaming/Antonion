from typing import Union

from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from telegram import User

from app.internal.user.db.models import TelegramUser
from app.internal.user.domain.interfaces import IFriendRequestRepository


class FriendRequestService:
    def __init__(self, request_repo: IFriendRequestRepository):
        self._request_repo = request_repo

    def get_usernames_to_friends(self, user: Union[User, TelegramUser]) -> QuerySet[str]:
        return self._request_repo.get_usernames_to_friends(user.id)

    def create(self, source: TelegramUser, destination: TelegramUser) -> bool:
        if self._request_repo.exists(source, destination):
            return False

        self._request_repo.create(source, destination)

        return True

    def try_reject(self, source: TelegramUser, destination: TelegramUser) -> bool:
        return self._request_repo.remove(source, destination)

    def try_accept(self, source: TelegramUser, destination: TelegramUser) -> bool:
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

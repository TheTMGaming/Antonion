from typing import Optional, Union

from django.db.models import QuerySet

from app.internal.user.db.models import FriendRequest, TelegramUser
from app.internal.user.domain.interfaces import IFriendRequestRepository


class FriendRequestRepository(IFriendRequestRepository):
    def create(self, source: TelegramUser, destination: TelegramUser) -> FriendRequest:
        return FriendRequest.objects.create(source=source, destination=destination)

    def get(self, source: TelegramUser, destination: TelegramUser) -> Optional[FriendRequest]:
        return self._get(source, destination).first()

    def exists(self, source: TelegramUser, destination: TelegramUser) -> bool:
        return self._get(source, destination).exists()

    def remove(self, source: TelegramUser, destination: TelegramUser) -> bool:
        return bool(self._get(source, destination).delete())

    def get_usernames_to_friends(self, user_id: Union[int, str]) -> QuerySet[str]:
        return FriendRequest.objects.filter(destination__id=user_id).values_list("source__username", flat=True)

    def _get(self, source: TelegramUser, destination: TelegramUser) -> QuerySet:
        return FriendRequest.objects.filter(source=source, destination=destination)

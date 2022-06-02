from typing import Optional, Union

from django.conf import settings
from django.db.models import QuerySet

from app.internal.user.db.models import TelegramUser
from app.internal.user.db.repositories.TelegramUserFields import TelegramUserFields
from app.internal.user.domain.interfaces import IFriendRepository, ITelegramUserRepository


class TelegramUserRepository(ITelegramUserRepository, IFriendRepository):
    def try_add_or_update_user(self, user_id: Union[int, str], username: str, first_name: str, last_name: str) -> bool:
        attributes = {
            TelegramUserFields.USERNAME: username,
            TelegramUserFields.FIRST_NAME: first_name,
            TelegramUserFields.LAST_NAME: last_name,
        }

        obj, was_added = TelegramUser.objects.update_or_create(id=user_id, defaults=attributes)

        return was_added

    def get_user(self, identifier: Union[int, str]) -> TelegramUser:
        param = (
            {TelegramUserFields.ID: int(identifier)}
            if str(identifier).isdigit()
            else {TelegramUserFields.USERNAME: str(identifier)}
        )

        return TelegramUser.objects.filter(**param).select_related("secret_key").first()

    def get_user_by_credentials(self, username: str, password: str) -> Optional[TelegramUser]:
        return TelegramUser.objects.filter(username=username, password=self._hash(password)).first()

    def get_friend(self, user_id: Union[int, str], identifier: Union[int, str]) -> Optional[TelegramUser]:
        param = (
            {TelegramUserFields.ID: int(identifier)}
            if str(identifier).isdigit()
            else {TelegramUserFields.USERNAME: str(identifier)}
        )

        return TelegramUser.objects.filter(friends__id=user_id, **param).first()

    def get_friends(self, user_id: Union[int, str]) -> QuerySet[TelegramUser]:
        return TelegramUser.objects.filter(friends__id=user_id).all()

    def is_friend_exists(self, user_id: Union[int, str], friend_id: Union[int, str]) -> bool:
        return TelegramUser.objects.filter(id=user_id, friends__id=friend_id).exists()

    def remove(self, source: TelegramUser, friend: TelegramUser) -> None:
        source.friends.remove(friend)

    def update_phone(self, user_id: Union[int, str], value: str) -> None:
        TelegramUser.objects.filter(id=user_id).update(phone=value)

    def update_password(self, user_id: Union[int, str], value: str) -> None:
        TelegramUser.objects.filter(id=user_id).update(password=self._hash(value))

    @staticmethod
    def _hash(password: str) -> str:
        return settings.HASHER.encode(password, settings.SALT)

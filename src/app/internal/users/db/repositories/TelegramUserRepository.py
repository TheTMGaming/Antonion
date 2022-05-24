from typing import Optional, Union

from django.db.models import QuerySet
from telegram import User

from app.internal.users.db.models import TelegramUser
from app.internal.users.db.repositories.TelegramUserFields import TelegramUserFields


class TelegramUserRepository:
    def try_add_or_update_user(self, user: User) -> bool:
        attributes = {
            TelegramUserFields.USERNAME: user.username,
            TelegramUserFields.FIRST_NAME: user.first_name,
            TelegramUserFields.LAST_NAME: user.last_name,
        }

        obj, was_added = TelegramUser.objects.update_or_create(id=user.id, defaults=attributes)

        return was_added

    def get_user(self, identifier: Union[int, str]) -> TelegramUser:
        param = (
            {TelegramUserFields.ID: int(identifier)}
            if str(identifier).isdigit()
            else {TelegramUserFields.USERNAME: str(identifier)}
        )

        return TelegramUser.objects.filter(**param).select_related("secret_key").first()

    def get_user_by_credentials(self, username: str, password: str) -> Optional[TelegramUser]:
        return TelegramUser.objects.get_by_credentials(username, password).first()

    def is_user_exist(self, user_id: Union[int, str]) -> bool:
        return bool(self.get_user(user_id))

    def get_friend(self, user: TelegramUser, identifier: Union[int, str]) -> Optional[TelegramUser]:
        param = (
            {TelegramUserFields.ID: int(identifier)}
            if str(identifier).isdigit()
            else {TelegramUserFields.USERNAME: str(identifier)}
        )

        return user.friends.filter(**param).first()

    def get_friends(self, user: TelegramUser) -> QuerySet[TelegramUser]:
        return user.friends.all()

    def is_friend_exists(self, user: TelegramUser, friend: TelegramUser) -> bool:
        return user.friends.filter(pk=friend.pk).exists()

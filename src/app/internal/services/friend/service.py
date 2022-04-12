from typing import Dict, Optional, Union

from django.db.models import QuerySet

from app.internal.models.user import TelegramUser
from app.internal.services.user.TelegramUserFields import TelegramUserFields


def get_friend(user: TelegramUser, identifier: Union[int, str]) -> Optional[TelegramUser]:
    param = (
        {TelegramUserFields.ID: int(identifier)}
        if str(identifier).isdigit()
        else {TelegramUserFields.USERNAME: str(identifier)}
    )

    return get_friends(user).filter(**param).first()


def get_friends(user: TelegramUser) -> QuerySet[TelegramUser]:
    return user.friends.all()


def get_friends_with_enums(user: TelegramUser) -> Dict[int, TelegramUser]:
    return dict((num, friend) for num, friend in enumerate(get_friends(user), 1))


def exists_friend(user: TelegramUser, friend: TelegramUser) -> bool:
    return friend in get_friends(user)

from django.db.models import QuerySet

from app.internal.models.user import TelegramUser


def get_friends(user: TelegramUser) -> QuerySet[TelegramUser]:
    return user.friends.all()


def exists_friend(user: TelegramUser, friend: TelegramUser) -> bool:
    return friend in get_friends(user)

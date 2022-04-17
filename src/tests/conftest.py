from typing import List

import pytest
from telegram import User

from app.internal.models.user import TelegramUser


@pytest.fixture(scope="function")
def first_user(user_id=1337, first_name="Вася", last_name="Пупкин", username="geroj") -> User:
    return User(id=user_id, first_name=first_name, last_name=last_name, username=username, is_bot=False)


@pytest.fixture(scope="function")
def second_user(user_id=228, first_name="Петька", last_name="Ас", username="very_metkij") -> User:
    return User(id=user_id, first_name=first_name, last_name=last_name, username=username, is_bot=False)


@pytest.fixture(scope="function")
def third_user(user_id=1111, first_name="Ваня", last_name="Чоткий", username="very_big_pig") -> User:
    return User(id=user_id, first_name=first_name, last_name=last_name, username=username, is_bot=False)


@pytest.fixture(scope="function")
def users(first_user: User, second_user: User, third_user: User) -> List[User]:
    return [first_user, second_user, third_user]


@pytest.fixture(scope="function")
def telegram_user(first_user: User) -> TelegramUser:
    user = TelegramUser.objects.filter(id=first_user.id)

    return TelegramUser.objects.create(
        id=first_user.id, username=first_user.username, first_name=first_user.first_name, last_name=first_user.last_name
    ) if not user else user


@pytest.fixture(scope="function")
def telegram_users(users: List[User]) -> List[TelegramUser]:
    return [
        TelegramUser.objects.create(
            id=user.id, username=user.username, first_name=user.first_name, last_name=user.last_name
        )
        for user in users if not TelegramUser.objects.filter(id=user.id)
    ]

from typing import List

import pytest
from telegram import User


@pytest.fixture(scope="function")
def first_user(user_id=1337, first_name="Вася", last_name="Пупкин", username="geroj") -> User:
    return User(id=user_id, first_name=first_name, last_name=last_name, username=username, is_bot=False)


@pytest.fixture(scope="function")
def second_user(user_id=228, first_name="Петька", last_name="Ас", username="very_metkij") -> User:
    return User(id=user_id, first_name=first_name, last_name=last_name, username=username, is_bot=False)


@pytest.fixture(scope="function")
def users(first_user: User, second_user: User) -> List[User]:
    return [first_user, second_user]

from typing import List
from unittest.mock import MagicMock

import pytest
from telegram import User

from app.internal.models.user import TelegramUser
from app.internal.transport.bot.modules.user import handle_start


@pytest.mark.django_db
@pytest.mark.integration
def test_start(update: MagicMock, user: User) -> None:
    handle_start(update, None)

    assert TelegramUser.objects.filter(
        id=user.id, first_name=user.first_name, last_name=user.last_name, username=user.username
    ).exists()


@pytest.mark.django_db
@pytest.mark.integration
def test_update(update: MagicMock, telegram_user: TelegramUser, user: User) -> None:
    user.username = user.username[::-1]
    user.first_name = user.first_name[::-1]
    user.last_name = user.last_name[::-1]

    update.effective_user = user

    handle_start(update, None)

    assert TelegramUser.objects.filter(
        id=telegram_user.id, first_name=user.first_name, last_name=user.last_name, username=user.username
    ).exists()


# @pytest.mark.django_db
# @pytest.mark.integration
# @pytest.mark.parametrize(
#     ["args", "is_set"],
#     [
#         [["88005553535"], True],
#         [["88005553535         "], True],
#         [["88005553535", " ", " "], True],
#         [["8", "800", "555", "35", "35"], True],
#         [["88005553535", "a", "b"], True],
#         [["                "], False],
#         [[" ", " ", " ", " "], False],
#         [[], False],
#         [["aaaaaaaaaaa"], False],
#         [["8800"], False],
#         [["88005553535", "1", "2"], False],
#         [["a", "b", "88005553535"], False],
#         [["        88005553535"], False],
#         [["aaa        88005553535"], False],
#         [[" ", " ", "88005553535"], False],
#     ],
# )
# def test_set_phone(
#     update: MagicMock, context: MagicMock, telegram_user: TelegramUser, args: List[str], is_set: bool
# ) -> None:
#     context.args = args
#
#     handle_set_phone(update, context)
#
#     actual = TelegramUser.objects.get(id=telegram_user.id)
#
#     assert is_set and actual.phone is not None or not is_set and actual.phone is None

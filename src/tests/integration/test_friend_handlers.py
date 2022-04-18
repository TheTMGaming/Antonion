from typing import List
from unittest.mock import MagicMock

import pytest
from telegram import User

from app.internal.models.user import TelegramUser
from app.internal.transport.bot.modules.friends import handle_add_friend, handle_friends, handle_remove_friend


@pytest.mark.django_db
@pytest.mark.integration
def test_adding(update: MagicMock, context: MagicMock, telegram_users_with_phone: List[TelegramUser]) -> None:
    user, friend_1, friend_2 = telegram_users_with_phone[0], telegram_users_with_phone[1], telegram_users_with_phone[2]

    for identifier in [friend_1.id, friend_2.username]:
        context.args = [str(identifier)]
        handle_add_friend(update, context)

    assert list(user.friends.all()) == [friend_1, friend_2]


@pytest.mark.django_db
@pytest.mark.integration
def test_adding_self(update: MagicMock, context: MagicMock, telegram_user_with_phone: TelegramUser) -> None:
    context.args = [str(telegram_user_with_phone.id)]

    handle_add_friend(update, context)

    assert telegram_user_with_phone.friends.count() == 0


@pytest.mark.django_db
@pytest.mark.integration
def test_adding_already_exist(
    update: MagicMock, context: MagicMock, telegram_users_with_phone: List[TelegramUser]
) -> None:
    user, friend = telegram_users_with_phone[0], telegram_users_with_phone[1]

    context.args = [str(friend.id)]

    for _ in range(3):
        handle_add_friend(update, context)

    assert user.friends.count() == 1


@pytest.mark.django_db
@pytest.mark.integration
def test_adding_not_exist(update: MagicMock, context: MagicMock, telegram_user_with_phone: TelegramUser) -> None:
    context.args = ["-1"]

    handle_add_friend(update, context)

    assert telegram_user_with_phone.friends.count() == 0


@pytest.mark.django_db
@pytest.mark.integration
def test_removing(update: MagicMock, context: MagicMock, telegram_users_with_phone: List[TelegramUser]) -> None:
    user, friend = telegram_users_with_phone[0], telegram_users_with_phone[1]

    for identifier in [friend.id, friend.username]:
        context.args = [str(identifier)]

        user.friends.add(friend)
        handle_remove_friend(update, context)

        assert user.friends.count() == 0


@pytest.mark.django_db
@pytest.mark.integration
def test_removing_not_exist(
    update: MagicMock, context: MagicMock, telegram_users_with_phone: List[TelegramUser]
) -> None:
    user, friend = telegram_users_with_phone[0], telegram_users_with_phone[1]

    user.friends.add(friend)

    context.args = ["-1"]
    handle_remove_friend(update, context)

    assert user.friends.count() == 1


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_friends(update: MagicMock, context: MagicMock, telegram_users_with_phone: List[TelegramUser]) -> None:
    for friend in telegram_users_with_phone[1:]:
        telegram_users_with_phone[0].friends.add(friend)

    handle_friends(update, context)

    assert update.message.reply_text.call_count == len(telegram_users_with_phone) - 1


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_friends_not_exist(
    update: MagicMock, context: MagicMock, telegram_users_with_phone: List[TelegramUser]
) -> None:
    handle_friends(update, context)

    assert update.message.reply_text.call_count == 1

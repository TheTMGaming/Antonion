import pytest
from telegram import Update, User
from telegram.ext import CallbackContext

from app.internal.bank.db.models import BankAccount, Transaction
from app.internal.user.db.models import TelegramUser
from app.internal.user.presentation.handlers.bot.commands import (
    _RELATION_LIST_EMPTY,
    _UPDATING_DETAILS,
    _WELCOME as welcome_user,
    handle_me,
    handle_relations,
    handle_start,
)


@pytest.mark.django_db
@pytest.mark.integration
def test_start__adding(update: Update, user: User) -> None:
    handle_start(update, None)

    assert TelegramUser.objects.filter(
        id=user.id, first_name=user.first_name, last_name=user.last_name, username=user.username
    ).exists()
    update.message.reply_text.assert_called_once_with(welcome_user.format(username=user.username))


@pytest.mark.django_db
@pytest.mark.integration
def test_start__updating(update: Update, telegram_user: TelegramUser, user: User) -> None:
    user.username = user.username[::-1]
    user.first_name = user.first_name[::-1]
    user.last_name = user.last_name[::-1]

    update.effective_user = user

    handle_start(update, None)

    assert TelegramUser.objects.filter(
        id=telegram_user.id, first_name=user.first_name, last_name=user.last_name, username=user.username
    ).exists()
    update.message.reply_text.assert_called_once_with(_UPDATING_DETAILS)


@pytest.mark.django_db
@pytest.mark.integration
def test_me(update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser) -> None:
    handle_me(update, context)
    update.message.reply_text.assert_called_once()


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_relations(
    update: Update,
    context: CallbackContext,
    telegram_user_with_phone: TelegramUser,
    bank_account: BankAccount,
    another_account: BankAccount,
) -> None:
    Transaction.objects.create(source=bank_account, destination=another_account)

    handle_relations(update, context)

    update.message.reply_text.assert_called_once()


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_relations__list_is_empty(
    update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser
) -> None:
    handle_relations(update, context)

    update.message.reply_text.assert_called_once_with(_RELATION_LIST_EMPTY)

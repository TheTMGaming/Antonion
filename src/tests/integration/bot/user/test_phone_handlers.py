from re import sub

import pytest
from telegram import Update
from telegram.ext import CallbackContext

from app.internal.user.db.models import TelegramUser
from app.internal.user.presentation.handlers.bot.phone.conversation import (
    _INVALID_PHONE,
    _UPDATING_PHONE,
    _WELCOME,
    handle_phone,
    handle_phone_start,
)
from app.internal.user.presentation.handlers.bot.phone.PhoneStates import PhoneStates
from tests.conftest import CORRECT_PHONE_NUMBERS, WRONG_PHONE_NUMBERS
from tests.integration.bot.conftest import assert_conversation_end, assert_conversation_start


@pytest.mark.django_db
@pytest.mark.integration
def test_phone_start(update: Update, context: CallbackContext, telegram_user: TelegramUser) -> None:
    next_state = handle_phone_start(update, context)

    assert next_state == PhoneStates.INPUT
    assert_conversation_start(context)
    update.message.reply_text.assert_called_once_with(_WELCOME)


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize("phone", WRONG_PHONE_NUMBERS)
def test_phone__setting_error(
    update: Update, context: CallbackContext, telegram_user: TelegramUser, phone: str
) -> None:
    update.message.text = phone

    next_state = handle_phone(update, context)

    assert next_state == PhoneStates.INPUT
    update.message.reply_text.assert_called_once_with(_INVALID_PHONE)

    telegram_user.refresh_from_db(fields=["phone"])
    assert telegram_user.phone is None


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize("phone", WRONG_PHONE_NUMBERS)
def test_phone__wrong(update: Update, context: CallbackContext, telegram_user: TelegramUser, phone: str) -> None:
    update.message.text = phone

    next_state = handle_phone(update, context)
    telegram_user.refresh_from_db()

    assert next_state == PhoneStates.INPUT
    update.message.reply_text.assert_called_once_with(_INVALID_PHONE)
    assert telegram_user.phone is None


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize("phone", CORRECT_PHONE_NUMBERS)
def test_phone(update: Update, context: CallbackContext, telegram_user: TelegramUser, phone: str) -> None:
    update.message.text = phone

    next_state = handle_phone(update, context)
    telegram_user.refresh_from_db()

    assert_conversation_end(next_state, context)
    update.message.reply_text.assert_called_once_with(_UPDATING_PHONE)
    assert telegram_user.phone == "+7" + sub(r"\D", "", phone)[1:]

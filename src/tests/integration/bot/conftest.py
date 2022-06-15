from unittest.mock import MagicMock

import pytest
from django.conf import settings
from telegram import PhotoSize, Update, User
from telegram.ext import CallbackContext, ConversationHandler

from app.internal.general.bot.handlers import COMMAND, IN_CONVERSATION


@pytest.fixture(scope="function")
def update(user: User, photo: PhotoSize) -> Update:
    delete = MagicMock()
    delete.return_value = None

    message = MagicMock()
    message.reply_text.return_value = None
    message.reply_document.return_value = None
    message.text = ""
    message.delete = delete
    message.photo = [photo]

    update = MagicMock()
    update.effective_user = user
    update.message = message

    return update


@pytest.fixture(scope="function")
def context() -> CallbackContext:
    bot = MagicMock()
    bot.send_message.return_value = None
    bot.send_photo.return_value = None

    context = MagicMock()
    context.args = []
    context.user_data = dict()
    context.bot = bot

    return context


@pytest.fixture(scope="function")
def photo() -> PhotoSize:
    photo = MagicMock()

    file = MagicMock()
    file.download_as_bytearray.return_value = b"123"

    photo.file_size = settings.MAX_SIZE_PHOTO_BYTES - 1
    photo.get_file.return_value = file
    photo.file_unique_id = "Super unique id"

    return photo


def assert_conversation_end(next_state: int, contex: CallbackContext) -> None:
    assert next_state == ConversationHandler.END
    assert len(contex.user_data) == 0


def assert_conversation_start(context: CallbackContext) -> None:
    assert IN_CONVERSATION in context.user_data
    assert context.user_data[IN_CONVERSATION] is True
    assert COMMAND in context.user_data

from unittest.mock import MagicMock

from telegram.ext import ConversationHandler

from app.internal.transport.bot.modules.general import COMMAND, IN_CONVERSATION


def assert_conversation_end(next_state: int, contex: MagicMock) -> None:
    assert next_state == ConversationHandler.END
    assert len(contex.user_data) == 0


def assert_conversation_start(context: MagicMock) -> None:
    assert IN_CONVERSATION in context.user_data
    assert context.user_data[IN_CONVERSATION] is True
    assert COMMAND in context.user_data

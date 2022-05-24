from telegram.ext import CallbackContext, ConversationHandler

from app.internal.bot.modules.general import COMMAND, IN_CONVERSATION


def assert_conversation_end(next_state: int, contex: CallbackContext) -> None:
    assert next_state == ConversationHandler.END
    assert len(contex.user_data) == 0


def assert_conversation_start(context: CallbackContext) -> None:
    assert IN_CONVERSATION in context.user_data
    assert context.user_data[IN_CONVERSATION] is True
    assert COMMAND in context.user_data

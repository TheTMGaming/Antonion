from unittest.mock import MagicMock

import pytest
from telegram.ext import ConversationHandler

from app.internal.transport.bot.modules.cancel import _CANCEL_OPERATION, handle_cancel


@pytest.mark.integration
def test_cancel(update: MagicMock, context: MagicMock) -> None:
    for i in range(10):
        context.user_data[str(i)] = None

    next_state = handle_cancel(update, context)

    assert next_state == ConversationHandler.END
    update.message.reply_text.assert_called_once_with(_CANCEL_OPERATION)
    assert len(context.user_data) == 0

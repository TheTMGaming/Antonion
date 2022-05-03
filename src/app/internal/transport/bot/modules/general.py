from typing import List

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler

_CANCEL_OPERATION = "Не хочешь разговаривать - ну и, ладно. Я не обидчивый :("
IN_CONVERSATION = "in_conversation"
COMMAND = "command"


def handle_cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(_CANCEL_OPERATION)

    context.user_data.clear()

    return ConversationHandler.END


def mark_begin_conversation(context: CallbackContext, command: List[str]) -> None:
    context.user_data[IN_CONVERSATION] = True
    context.user_data[COMMAND] = "".join(command)


cancel = CommandHandler("cancel", handle_cancel)

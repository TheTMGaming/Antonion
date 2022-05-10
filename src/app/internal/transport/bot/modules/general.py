from typing import List

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler

_CANCEL_OPERATION = "Не хочешь разговаривать - ну и, ладно. Я не обидчивый :("
IN_CONVERSATION = "in_conversation"
COMMAND = "command"


def handle_cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(_CANCEL_OPERATION)

    return mark_conversation_end(context)


def mark_conversation_start(context: CallbackContext, command: List[str]) -> None:
    context.user_data[IN_CONVERSATION] = True
    context.user_data[COMMAND] = "".join(command)


def mark_conversation_end(contex: CallbackContext) -> int:
    contex.user_data.clear()

    return ConversationHandler.END


cancel = CommandHandler("cancel", handle_cancel)

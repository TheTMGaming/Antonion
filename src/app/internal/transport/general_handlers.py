from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

_CANCEL_OPERATION = "Не хочешь разговаривать - ну и, ладно. Я не обидчивый :("


def handle_cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(_CANCEL_OPERATION)
    return ConversationHandler.END

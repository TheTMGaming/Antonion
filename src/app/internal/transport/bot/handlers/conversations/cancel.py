from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler

_CANCEL_OPERATION = "Не хочешь разговаривать - ну и, ладно. Я не обидчивый :("


def handle_cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(_CANCEL_OPERATION)

    context.user_data.clear()

    return ConversationHandler.END


cancel = CommandHandler("cancel", handle_cancel)

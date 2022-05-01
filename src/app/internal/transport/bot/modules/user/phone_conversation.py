from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, Filters, MessageHandler

from app.internal.services.user import try_set_phone
from app.internal.transport.bot.decorators import if_update_message_exist, if_user_exist
from app.internal.transport.bot.modules.cancel import cancel
from app.internal.transport.bot.modules.user.PhoneStates import PhoneStates

_WELCOME = "Введите, пожалуйста, номер телефона"
_UPDATING_PHONE = "Телефон обновил! Готовьтесь к захватывающему спаму!"
_INVALID_PHONE = "Я не могу сохранить эти кракозябры. Повторите попытку, либо /cancel"


@if_update_message_exist
@if_user_exist
def handle_phone_start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(_WELCOME)

    return PhoneStates.INPUT


@if_update_message_exist
def handle_phone(update: Update, context: CallbackContext) -> int:
    phone = update.message.text

    was_set = try_set_phone(update.effective_user.id, phone)
    if not was_set:
        update.message.reply_text(_INVALID_PHONE)
        return PhoneStates.INPUT

    update.message.reply_text(_UPDATING_PHONE)


phone_conversation = ConversationHandler(
    entry_points=[CommandHandler("phone", handle_phone_start)],
    states={PhoneStates.INPUT: [MessageHandler(Filters.text & ~Filters.command, handle_phone)]},
    fallbacks=[cancel],
)

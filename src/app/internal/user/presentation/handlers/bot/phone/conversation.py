from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, MessageHandler

from app.internal.general.bot.decorators import if_update_message_exists, if_user_exists, if_user_is_not_in_conversation
from app.internal.general.bot.filters import TEXT
from app.internal.general.bot.handlers import cancel, mark_conversation_end, mark_conversation_start
from app.internal.user.db.repositories import SecretKeyRepository, TelegramUserRepository
from app.internal.user.domain.services import TelegramUserService
from app.internal.user.presentation.handlers.bot.phone.PhoneStates import PhoneStates

_WELCOME = "Введите, пожалуйста, номер телефона"
_UPDATING_PHONE = "Телефон обновил! Готовьтесь к захватывающему спаму!"
_INVALID_PHONE = "Я не могу сохранить эти кракозябры. Повторите попытку, либо /cancel"

_user_service = TelegramUserService(user_repo=TelegramUserRepository(), secret_key_repo=SecretKeyRepository())


@if_update_message_exists
@if_user_exists
@if_user_is_not_in_conversation
def handle_phone_start(update: Update, context: CallbackContext) -> int:
    mark_conversation_start(context, entry_point.command)

    update.message.reply_text(_WELCOME)

    return PhoneStates.INPUT


@if_update_message_exists
def handle_phone(update: Update, context: CallbackContext) -> int:
    phone = update.message.text

    was_set = _user_service.try_set_phone(update.effective_user.id, phone)
    if not was_set:
        update.message.reply_text(_INVALID_PHONE)
        return PhoneStates.INPUT

    update.message.reply_text(_UPDATING_PHONE)

    return mark_conversation_end(context)


entry_point = CommandHandler("phone", handle_phone_start)


phone_conversation = ConversationHandler(
    entry_points=[entry_point],
    states={PhoneStates.INPUT: [MessageHandler(TEXT, handle_phone)]},
    fallbacks=[cancel],
)

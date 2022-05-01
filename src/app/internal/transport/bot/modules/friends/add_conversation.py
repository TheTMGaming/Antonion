from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, Filters, MessageHandler

from app.internal.services.friend import is_friend_exist
from app.internal.services.user import get_user
from app.internal.transport.bot.decorators import if_phone_is_set, if_update_message_exist, if_user_exist
from app.internal.transport.bot.modules.cancel import cancel
from app.internal.transport.bot.modules.filters import TEXT
from app.internal.transport.bot.modules.friends.FriendStates import FriendStates

_WELCOME = "Введите никнейм или идентификатор пользователя"
_STUPID_CHOICE_SELF_ERROR = "Это же ваш профиль! Повторите попытку, либо /cancel"
_USER_NOT_FOUND_ERROR = "В нашей базе нет такого пользователя! Повторите попытку, либо /cancel"
_ALREADY_EXIST_ERROR = "Так он уже твой друг! Смысл было меня отвлекать от важных дел! Повторите попытку, либо /cancel"
_ADD_SUCCESS = "Ураа! Да прибудет денюж... в смысле дружба!"


@if_update_message_exist
@if_user_exist
@if_phone_is_set
def handle_add_friend_start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(_WELCOME)

    return FriendStates.INPUT


@if_update_message_exist
def handle_add_friend(update: Update, context: CallbackContext) -> int:
    friend_identifier = "".join(update.message.text)

    user = get_user(update.effective_user.id)
    friend = get_user(friend_identifier)

    if user == friend:
        update.message.reply_text(_STUPID_CHOICE_SELF_ERROR)
        return FriendStates.INPUT

    if not friend:
        update.message.reply_text(_USER_NOT_FOUND_ERROR)
        return FriendStates.INPUT

    if is_friend_exist(user, friend):
        update.message.reply_text(_ALREADY_EXIST_ERROR)
        return FriendStates.INPUT

    user.friends.add(friend)
    update.message.reply_text(_ADD_SUCCESS)

    return ConversationHandler.END


add_friend_conversation = ConversationHandler(
    entry_points=[CommandHandler("add_friend", handle_add_friend_start)],
    states={FriendStates.INPUT: [MessageHandler(TEXT, handle_add_friend)]},
    fallbacks=[cancel],
)

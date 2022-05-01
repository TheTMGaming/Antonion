from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, MessageHandler

from app.internal.services.friend import get_friend
from app.internal.services.user import get_user
from app.internal.transport.bot.decorators import if_phone_is_set, if_update_message_exist, if_user_exist
from app.internal.transport.bot.modules.cancel import cancel
from app.internal.transport.bot.modules.filters import TEXT
from app.internal.transport.bot.modules.friends.FriendStates import FriendStates

_WELCOME = "Введите никнейм или идентификатор пользователя"
_INVALID_IDENTIFIER_OR_LIST_EMPTY_ERROR = (
    "Такого страдальца я не знаю, либо вы с ним не знакомы! Повторите попытку, либо /cancel"
)
_REMOVE_SUCCESS = "Товарищ покинул ваш чат..."


@if_update_message_exist
@if_user_exist
@if_phone_is_set
def handle_rm_friend_start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(_WELCOME)

    return FriendStates.INPUT


@if_update_message_exist
def handle_rm_friend(update: Update, context: CallbackContext) -> int:
    friend_identifier = "".join(update.message.text)

    user = get_user(update.effective_user.id)
    friend = get_friend(user, friend_identifier)

    if not friend:
        update.message.reply_text(_INVALID_IDENTIFIER_OR_LIST_EMPTY_ERROR)
        return FriendStates.INPUT

    user.friends.remove(friend)
    update.message.reply_text(_REMOVE_SUCCESS)

    return ConversationHandler.END


rm_friend_conversation = ConversationHandler(
    entry_points=[CommandHandler("rm_friend", handle_rm_friend_start)],
    states={
        FriendStates.INPUT: [MessageHandler(TEXT, handle_rm_friend)],
    },
    fallbacks=[cancel],
)

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, MessageHandler

from app.internal.models.user import TelegramUser
from app.internal.services.friend import is_friend_exist, try_create_friend_request
from app.internal.services.user import get_user
from app.internal.transport.bot.decorators import (
    if_phone_is_set,
    if_update_message_exist,
    if_user_exist,
    if_user_is_not_in_conversation,
)
from app.internal.transport.bot.modules.filters import TEXT
from app.internal.transport.bot.modules.friends.FriendStates import FriendStates
from app.internal.transport.bot.modules.general import cancel, mark_conversation_end, mark_conversation_start

_WELCOME = "Введите никнейм или идентификатор пользователя"
_STUPID_CHOICE_SELF_ERROR = "Это же ваш профиль! Повторите попытку, либо /cancel"
_USER_NOT_FOUND_ERROR = "В нашей базе нет такого пользователя! Повторите попытку, либо /cancel"
_ALREADY_EXIST_ERROR = "Так он уже твой друг! Смысл было меня отвлекать от важных дел! Повторите попытку, либо /cancel"
_REQUEST_ALREADY_EXIST_ERROR = "Вы уже отправили заявку данному пользователю! Введите другой никнейм, либо /cancel"
_REQUEST_SUCCESS = "Заявка отправлена! Да прибудет денюж... в смысле дружба!"
_NOTIFICATION_MESSAGE = "С вами хочет познакомиться {username} ({name}). Используйте команду /accept"


@if_update_message_exist
@if_user_exist
@if_phone_is_set
@if_user_is_not_in_conversation
def handle_add_friend_start(update: Update, context: CallbackContext) -> int:
    mark_conversation_start(context, entry_point.command)

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

    if not try_create_friend_request(user, friend):
        update.message.reply_text(_REQUEST_ALREADY_EXIST_ERROR)
        return FriendStates.INPUT

    update.message.reply_text(_REQUEST_SUCCESS)

    context.bot.send_message(
        chat_id=friend.id,
        text=get_notification(user),
    )

    return mark_conversation_end(context)


def get_notification(source: TelegramUser) -> str:
    return _NOTIFICATION_MESSAGE.format(
        username=source.username, name=" ".join(filter(bool, [source.last_name, source.first_name]))
    )


entry_point = CommandHandler("add", handle_add_friend_start)


add_friend_conversation = ConversationHandler(
    entry_points=[entry_point],
    states={FriendStates.INPUT: [MessageHandler(TEXT, handle_add_friend)]},
    fallbacks=[cancel],
)

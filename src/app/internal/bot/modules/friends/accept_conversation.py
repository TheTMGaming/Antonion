from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, MessageHandler

from app.internal.bot.decorators import (
    if_phone_is_set,
    if_update_message_exists,
    if_user_exist,
    if_user_is_not_in_conversation,
)
from app.internal.bot.modules.filters import INT
from app.internal.bot.modules.friends.FriendStates import FriendStates
from app.internal.bot.modules.friends.users_to_friends_sender import send_username_list
from app.internal.bot.modules.general import cancel, mark_conversation_end, mark_conversation_start
from app.internal.users.db.models import TelegramUser
from app.internal.users.db.repositories import FriendRequestRepository, SecretKeyRepository, TelegramUserRepository
from app.internal.users.domain.services import FriendBotService, TelegramUserBotService

_WELCOME = "Выберите из списка того, с кем хотите иметь дело:\n\n"
_USERNAME_VARIANT = "{num}) {username}"
_LIST_EMPTY = "На данный момент нет заявок в друзья :("
_STUPID_CHOICE = "Нет такого в списке. Повторите попытку, либо /cancel"
_FRIEND_CANCEL = "Приятель уже не хочет с вами дружить :("
_ACCEPT_SUCCESS = "Ураа. Теперь вы друзья с {username}"

_USERNAMES_SESSION = "username_list"

_user_service = TelegramUserBotService(user_repo=TelegramUserRepository(), secret_key_repo=SecretKeyRepository())
_friend_service = FriendBotService(friend_repo=TelegramUserRepository(), request_repo=FriendRequestRepository())


@if_update_message_exists
@if_user_exist
@if_phone_is_set
@if_user_is_not_in_conversation
def handle_accept_start(update: Update, context: CallbackContext) -> int:
    mark_conversation_start(context, entry_point.command)

    return send_username_list(update, context, _LIST_EMPTY, _USERNAMES_SESSION, _WELCOME)


@if_update_message_exists
def handle_accept(update: Update, context: CallbackContext) -> int:
    username = context.user_data[_USERNAMES_SESSION].get(int(update.message.text))

    if not username:
        update.message.reply_text(_STUPID_CHOICE)
        return FriendStates.INPUT

    user = _user_service.get_user(update.effective_user.id)
    friend = _user_service.get_user(username)

    if not _friend_service.try_accept_friend(friend, user):
        update.message.reply_text(_FRIEND_CANCEL)
        return mark_conversation_end(context)

    update.message.reply_text(get_notification(friend))
    context.bot.send_message(chat_id=friend.id, text=get_notification(user))

    return mark_conversation_end(context)


def get_notification(user: TelegramUser) -> str:
    return _ACCEPT_SUCCESS.format(username=user.username)


entry_point = CommandHandler("accept", handle_accept_start)


accept_conversation = ConversationHandler(
    entry_points=[entry_point],
    states={
        FriendStates.INPUT: [MessageHandler(INT, handle_accept)],
    },
    fallbacks=[cancel],
)

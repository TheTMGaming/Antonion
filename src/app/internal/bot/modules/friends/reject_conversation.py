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
from app.internal.bot.modules.friends.username_list_sender import send_username_list
from app.internal.bot.modules.general import cancel, mark_conversation_end, mark_conversation_start
from app.internal.users.db.models import TelegramUser
from app.internal.users.db.repositories import FriendRequestRepository, TelegramUserRepository
from app.internal.users.domain.services import FriendService

_WELCOME = "Выберите из списка того, с кем не хотите иметь дело:\n\n"
_LIST_EMPTY = "На данный момент нет заявок в друзья :("
_STUPID_CHOICE = "Нет такого в списке. Повторите попытку, либо /cancel"
_FRIEND_CANCEL = "Приятель уже не хочет с вами дружить :( Выберите другого пользователя, либо /cancel"
_REJECT_SUCCESS = "Заявка улетела в далёкие края"
_REJECT_MESSAGE = "Пользователь {username} отменил вашу заявку в друзья :("

_USERNAMES_SESSION = "username_list"


_user_repo = TelegramUserRepository()
_friend_service = FriendService(friend_repo=_user_repo, request_repo=FriendRequestRepository())


@if_update_message_exists
@if_user_exist
@if_phone_is_set
@if_user_is_not_in_conversation
def handle_reject_start(update: Update, context: CallbackContext) -> int:
    mark_conversation_start(context, entry_point.command)

    return send_username_list(update, context, _LIST_EMPTY, _USERNAMES_SESSION, _WELCOME)


@if_update_message_exists
def handle_reject(update: Update, context: CallbackContext) -> int:
    username = context.user_data[_USERNAMES_SESSION].get(int(update.message.text))

    if not username:
        update.message.reply_text(_STUPID_CHOICE)
        return FriendStates.INPUT

    user = _user_repo.get_user(update.effective_user.id)
    friend = _user_repo.get_user(username)

    _friend_service.reject_friend_request(friend, user)

    update.message.reply_text(_REJECT_SUCCESS)
    context.bot.send_message(chat_id=friend.id, text=get_notification(user))

    return mark_conversation_end(context)


def get_notification(source: TelegramUser) -> str:
    return _REJECT_MESSAGE.format(username=source.username)


entry_point = CommandHandler("reject", handle_reject_start)


reject_conversation = ConversationHandler(
    entry_points=[entry_point],
    states={
        FriendStates.INPUT: [MessageHandler(INT, handle_reject)],
    },
    fallbacks=[cancel],
)

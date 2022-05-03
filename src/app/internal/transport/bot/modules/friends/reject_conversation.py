from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, MessageHandler

from app.internal.models.user import TelegramUser
from app.internal.services.friend import reject_friend_request
from app.internal.services.user import get_user
from app.internal.transport.bot.decorators import if_phone_is_set, if_update_message_exist, if_user_exist, \
    if_user_is_not_in_conversation
from app.internal.transport.bot.modules.general import cancel, mark_begin_conversation
from app.internal.transport.bot.modules.filters import INT
from app.internal.transport.bot.modules.friends.FriendStates import FriendStates
from app.internal.transport.bot.modules.friends.username_list_sender import send_username_list

_WELCOME = "Выберите из списка того, с кем не хотите иметь дело:\n\n"
_LIST_EMPTY = "На данный момент нет заявок в друзья :("
_STUPID_CHOICE = "Нет такого в списке. Повторите попытку, либо /cancel"
_FRIEND_CANCEL = "Приятель уже не хочет с вами дружить :( Выберите другого пользователя, либо /cancel"
_REJECT_SUCCESS = "Заявка улетела в далёкие края"
_REJECT_MESSAGE = "Пользователь {username} отменил вашу заявку в друзья :("

_USERNAMES_SESSION = "username_list"


@if_update_message_exist
@if_user_exist
@if_phone_is_set
@if_user_is_not_in_conversation
def handle_reject_start(update: Update, context: CallbackContext) -> int:
    mark_begin_conversation(context, entry_point.command)

    return send_username_list(update, context, _LIST_EMPTY, _USERNAMES_SESSION, _WELCOME)


@if_update_message_exist
def handle_reject(update: Update, context: CallbackContext) -> int:
    username = context.user_data[_USERNAMES_SESSION].get(int(update.message.text))
    context.user_data.clear()

    if not username:
        update.message.reply_text(_STUPID_CHOICE)
        return FriendStates.INPUT

    user = get_user(update.effective_user.id)
    friend = get_user(username)

    reject_friend_request(friend, user)

    update.message.reply_text(_REJECT_SUCCESS)
    context.bot.send_message(chat_id=friend.id, text=get_notification(user))

    return ConversationHandler.END


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

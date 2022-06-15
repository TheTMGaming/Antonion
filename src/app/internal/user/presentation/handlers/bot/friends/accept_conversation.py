from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, MessageHandler

from app.internal.general.bot.decorators import authorize_user, is_message_defined, is_not_user_in_conversation
from app.internal.general.bot.filters import INT
from app.internal.general.bot.handlers import cancel, mark_conversation_end, mark_conversation_start
from app.internal.general.services import request_service, user_service
from app.internal.user.db.models import TelegramUser
from app.internal.user.presentation.handlers.bot.friends.FriendStates import FriendStates
from app.internal.user.presentation.handlers.bot.friends.general import send_username_list

_WELCOME = "Выберите из списка того, с кем хотите иметь дело:\n\n"
_USERNAME_VARIANT = "{num}) {username}"
_LIST_EMPTY = "На данный момент нет заявок в друзья :("
_STUPID_CHOICE = "Нет такого в списке. Повторите попытку, либо /cancel"
_FRIEND_CANCEL = "Приятель уже не хочет с вами дружить :("
_ACCEPT_SUCCESS = "Ураа. Теперь вы друзья с {username}"

_USERNAMES_SESSION = "username_list"


@is_message_defined
@authorize_user()
@is_not_user_in_conversation
def handle_accept_start(update: Update, context: CallbackContext) -> int:
    mark_conversation_start(context, entry_point.command)

    return send_username_list(update, context, _LIST_EMPTY, _USERNAMES_SESSION, _WELCOME)


@is_message_defined
def handle_accept(update: Update, context: CallbackContext) -> int:
    username = context.user_data[_USERNAMES_SESSION].get(int(update.message.text))

    if not username:
        update.message.reply_text(_STUPID_CHOICE)
        return FriendStates.INPUT

    user = user_service.get_user(update.effective_user.id)
    friend = user_service.get_user(username)

    if not request_service.try_accept(friend, user):
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

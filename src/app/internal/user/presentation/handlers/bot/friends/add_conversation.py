from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, MessageHandler

from app.internal.general.bot.decorators import authorize_user, is_message_defined, is_not_user_in_conversation
from app.internal.general.bot.filters import TEXT
from app.internal.general.bot.handlers import cancel, mark_conversation_end, mark_conversation_start
from app.internal.general.services import friend_service, request_service, user_service
from app.internal.user.db.models import TelegramUser
from app.internal.user.presentation.handlers.bot.friends.FriendStates import FriendStates

_WELCOME = "Введите никнейм или идентификатор пользователя, либо /cancel"
_STUPID_CHOICE_SELF_ERROR = "Это же ваш профиль! Повторите попытку, либо /cancel"
_USER_NOT_FOUND_ERROR = "В нашей базе нет такого пользователя! Повторите попытку, либо /cancel"
_ALREADY_EXIST_ERROR = "Так он уже твой друг! Смысл было меня отвлекать от важных дел! Повторите попытку, либо /cancel"
_REQUEST_ALREADY_EXIST_ERROR = "Вы уже отправили заявку данному пользователю! Введите другой никнейм, либо /cancel"
_REQUEST_SUCCESS = "Заявка отправлена! Да прибудет денюж... в смысле дружба!"
_NOTIFICATION_MESSAGE = "С вами хочет познакомиться {username} ({name}). Используйте команду /accept"


@is_message_defined
@authorize_user()
@is_not_user_in_conversation
def handle_add_friend_start(update: Update, context: CallbackContext) -> int:
    mark_conversation_start(context, entry_point.command)

    update.message.reply_text(_WELCOME)

    return FriendStates.INPUT


@is_message_defined
def handle_add_friend(update: Update, context: CallbackContext) -> int:
    friend_identifier = "".join(update.message.text)

    user = user_service.get_user(update.effective_user.id)
    friend = user_service.get_user(friend_identifier)

    if user == friend:
        update.message.reply_text(_STUPID_CHOICE_SELF_ERROR)
        return FriendStates.INPUT

    if not friend:
        update.message.reply_text(_USER_NOT_FOUND_ERROR)
        return FriendStates.INPUT

    if friend_service.is_friend_exists(user, friend):
        update.message.reply_text(_ALREADY_EXIST_ERROR)
        return FriendStates.INPUT

    if not request_service.try_create(user, friend):
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

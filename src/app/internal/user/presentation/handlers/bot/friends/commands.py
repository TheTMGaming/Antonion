from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from app.internal.general.bot.decorators import authorize_user, is_message_defined, is_not_user_in_conversation
from app.internal.general.services import friend_service, request_service, user_service
from app.internal.user.presentation.handlers.bot.commands import get_user_details

_USER_NOT_FOUND_ERROR = "В нашей базе нет такого пользователя!"
_LIST_EMPTY_ERROR = "У вас пока что нет друзей:("
_STUPID_CHOICE_SELF_ERROR = "Это же ваш профиль!"

_FRIENDSHIP_WELCOME = "Список заявок в друзья:\n\n"
_FRIENDSHIPS_EMPTY = "На данный момент нет заявок в друзья :("


@is_message_defined
@authorize_user()
@is_not_user_in_conversation
def handle_friends(update: Update, context: CallbackContext) -> None:
    user = user_service.get_user(update.effective_user.id)

    friends = friend_service.get_friends(user)
    if len(friends) == 0:
        update.message.reply_text(_LIST_EMPTY_ERROR)
        return

    for details in map(get_user_details, friends):
        update.message.reply_text(details)


@is_message_defined
@authorize_user()
@is_not_user_in_conversation
def handle_friendships(update: Update, context: CallbackContext) -> None:
    usernames = request_service.get_usernames_to_friends(update.effective_user)

    update.message.reply_text(_FRIENDSHIP_WELCOME + "\n".join(usernames) if usernames else _FRIENDSHIPS_EMPTY)


friends_commands = [
    CommandHandler("friends", handle_friends),
    CommandHandler("friendships", handle_friendships),
]

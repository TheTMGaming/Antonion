from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from app.internal.services.friend import get_friends, get_friendship_username_list
from app.internal.services.user import get_user
from app.internal.transport.bot.decorators import if_phone_is_set, if_update_message_exist, if_user_exist, \
    if_user_is_not_in_conversation
from app.internal.transport.bot.modules.user.handlers import get_user_details

_USER_NOT_FOUND_ERROR = "В нашей базе нет такого пользователя!"
_LIST_EMPTY_ERROR = "У вас пока что нет друзей:("
_STUPID_CHOICE_SELF_ERROR = "Это же ваш профиль!"

_FRIENDSHIP_WELCOME = "Список заявок в друзья:\n\n"
_FRIENDSHIPS_EMPTY = "На данный момент нет заявок в друзья :("


@if_update_message_exist
@if_user_exist
@if_phone_is_set
@if_user_is_not_in_conversation
def handle_friends(update: Update, context: CallbackContext) -> None:
    user = get_user(update.effective_user.id)

    friends = get_friends(user)
    if len(friends) == 0:
        update.message.reply_text(_LIST_EMPTY_ERROR)
        return

    for details in (get_user_details(friend) for friend in friends):
        update.message.reply_text(details)


@if_update_message_exist
@if_user_exist
@if_phone_is_set
@if_user_is_not_in_conversation
def handle_friendships(update: Update, context: CallbackContext) -> None:
    usernames = get_friendship_username_list(update.effective_user.id)

    update.message.reply_text(_FRIENDSHIP_WELCOME + "\n".join(usernames) if usernames else _FRIENDSHIPS_EMPTY)


friends_commands = [
    CommandHandler("friends", handle_friends),
    CommandHandler("friendships", handle_friendships),
]

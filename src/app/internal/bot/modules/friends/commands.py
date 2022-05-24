from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from app.internal.bot.decorators import (
    if_phone_is_set,
    if_update_message_exists,
    if_user_exist,
    if_user_is_not_in_conversation,
)
from app.internal.bot.modules.user.handlers import get_user_details
from app.internal.users.db.repositories import FriendRequestRepository, TelegramUserRepository

_USER_NOT_FOUND_ERROR = "В нашей базе нет такого пользователя!"
_LIST_EMPTY_ERROR = "У вас пока что нет друзей:("
_STUPID_CHOICE_SELF_ERROR = "Это же ваш профиль!"

_FRIENDSHIP_WELCOME = "Список заявок в друзья:\n\n"
_FRIENDSHIPS_EMPTY = "На данный момент нет заявок в друзья :("


_user_repo = TelegramUserRepository()
_request_repo = FriendRequestRepository()


@if_update_message_exists
@if_user_exist
@if_phone_is_set
@if_user_is_not_in_conversation
def handle_friends(update: Update, context: CallbackContext) -> None:
    user = _user_repo.get_user(update.effective_user.id)

    friends = _user_repo.get_friends(user)
    if len(friends) == 0:
        update.message.reply_text(_LIST_EMPTY_ERROR)
        return

    for details in map(get_user_details, friends):
        update.message.reply_text(details)


@if_update_message_exists
@if_user_exist
@if_phone_is_set
@if_user_is_not_in_conversation
def handle_friendships(update: Update, context: CallbackContext) -> None:
    usernames = _request_repo.get_usernames_to_friends(update.effective_user.id)

    update.message.reply_text(_FRIENDSHIP_WELCOME + "\n".join(usernames) if usernames else _FRIENDSHIPS_EMPTY)


friends_commands = [
    CommandHandler("friends", handle_friends),
    CommandHandler("friendships", handle_friendships),
]

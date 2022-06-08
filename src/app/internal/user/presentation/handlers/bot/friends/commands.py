from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from app.internal.general.bot.decorators import (
    if_phone_was_set,
    if_update_message_exists,
    if_user_exists,
    if_user_is_not_in_conversation,
)
from app.internal.user.db.repositories import FriendRequestRepository, SecretKeyRepository, TelegramUserRepository
from app.internal.user.domain.services import FriendRequestService, FriendService, TelegramUserService
from app.internal.user.presentation.handlers.bot.commands import get_user_details

_USER_NOT_FOUND_ERROR = "В нашей базе нет такого пользователя!"
_LIST_EMPTY_ERROR = "У вас пока что нет друзей:("
_STUPID_CHOICE_SELF_ERROR = "Это же ваш профиль!"

_FRIENDSHIP_WELCOME = "Список заявок в друзья:\n\n"
_FRIENDSHIPS_EMPTY = "На данный момент нет заявок в друзья :("


_user_service = TelegramUserService(user_repo=TelegramUserRepository(), secret_key_repo=SecretKeyRepository())
_friend_service = FriendService(friend_repo=TelegramUserRepository())
_request_service = FriendRequestService(request_repo=FriendRequestRepository())


@if_update_message_exists
@if_user_exists
@if_phone_was_set
@if_user_is_not_in_conversation
def handle_friends(update: Update, context: CallbackContext) -> None:
    user = _user_service.get_user(update.effective_user.id)

    friends = _friend_service.get_friends(user)
    if len(friends) == 0:
        update.message.reply_text(_LIST_EMPTY_ERROR)
        return

    for details in map(get_user_details, friends):
        update.message.reply_text(details)


@if_update_message_exists
@if_user_exists
@if_phone_was_set
@if_user_is_not_in_conversation
def handle_friendships(update: Update, context: CallbackContext) -> None:
    usernames = _request_service.get_usernames_to_friends(update.effective_user)

    update.message.reply_text(_FRIENDSHIP_WELCOME + "\n".join(usernames) if usernames else _FRIENDSHIPS_EMPTY)


friends_commands = [
    CommandHandler("friends", handle_friends),
    CommandHandler("friendships", handle_friendships),
]

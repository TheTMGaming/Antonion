from telegram import Update
from telegram.ext import CallbackContext

from app.internal.services.friend import exists_friend, get_friend, get_friends
from app.internal.services.user import get_user
from app.internal.transport.bot.modules.user import get_user_details
from app.internal.transport.bot.modules.user.decorators import if_phone_is_set

_INVALID_IDENTIFIER_OR_LIST_EMPTY_ERROR = (
    "Такого страдальца я не знаю, либо их вообще нет... Проверьте введённый username/id!"
)
_ALREADY_EXIST_ERROR = "Так он уже твой друг! Смысл было меня отвлекать от важных дел!"
_ADD_SUCCESS = "Ураа! Да прибудет денюж... в смысле дружба!"
_REMOVE_SUCCESS = "Товарищ покинул ваш чат..."
_LIST_EMPTY_ERROR = "У вас пока что нет друзей:("
_STUPID_CHOICE_SELF_ERROR = "Это же ваш профиль!"


@if_phone_is_set
def handle_add_friend(update: Update, context: CallbackContext) -> None:
    user = get_user(update.effective_user.id)
    friend_identifier = "".join(context.args)

    friend = get_user(friend_identifier)

    if user == friend:
        update.message.reply_text(_STUPID_CHOICE_SELF_ERROR)
        return

    if not friend:
        update.message.reply_text(_INVALID_IDENTIFIER_OR_LIST_EMPTY_ERROR)
        return

    if exists_friend(user, friend):
        update.message.reply_text(_ALREADY_EXIST_ERROR)
        return

    user.friends.add(friend)
    update.message.reply_text(_ADD_SUCCESS)


@if_phone_is_set
def handle_remove_friend(update: Update, context: CallbackContext) -> None:
    user = get_user(update.effective_user.id)
    friend_identifier = "".join(context.args)

    friend = get_friend(user, friend_identifier)
    if not friend:
        update.message.reply_text(_INVALID_IDENTIFIER_OR_LIST_EMPTY_ERROR)
        return

    user.friends.remove(friend)
    update.message.reply_text(_REMOVE_SUCCESS)


@if_phone_is_set
def handle_friends(update: Update, context: CallbackContext) -> None:
    user = get_user(update.effective_user.id)

    friends = get_friends(user)
    if len(friends) == 0:
        update.message.reply_text(_LIST_EMPTY_ERROR)
        return

    for details in (get_user_details(friend) for friend in friends):
        update.message.reply_text(details)

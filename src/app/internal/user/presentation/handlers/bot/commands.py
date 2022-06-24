from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from app.internal.general.bot.decorators import authorize_user, is_message_defined, is_not_user_in_conversation
from app.internal.general.services import transaction_service, user_service
from app.internal.user.db.models import TelegramUser

_WELCOME = 'Привет, дорогой {username}. Рад приветствовать в "Банке мечты"!'
_UPDATING_DETAILS = "Всё пучком! Я обновил информацию о вас"
_DETAILS = "ID: {id}\n" "Ник: {username}\n" "Фамилия: {last_name}\n" "Имя: {first_name}\n" "Телефон: {phone}\n"

_RELATIONS_DETAILS = "Вот с этими людьми вы взаимодействовали:\n\n{usernames}"
_RELATION_POINT = "{number}) {username}"
_RELATION_LIST_EMPTY = "Похоже, что вы в танке... и ни с кеми не взаимодействовали"


@is_message_defined
def handle_start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user

    was_added = user_service.try_add_or_update_user(user)

    message = _WELCOME.format(username=user.username) if was_added else _UPDATING_DETAILS

    update.message.reply_text(message)


@is_message_defined
@authorize_user()
@is_not_user_in_conversation
def handle_me(update: Update, context: CallbackContext) -> None:
    user = user_service.get_user(update.effective_user.id)

    message = get_user_details(user)

    update.message.reply_text(message)


@is_message_defined
@authorize_user()
@is_not_user_in_conversation
def handle_relations(update: Update, context: CallbackContext) -> None:
    usernames = list(enumerate(transaction_service.get_related_usernames(update.effective_user.id), start=1))

    if not usernames:
        update.message.reply_text(_RELATION_LIST_EMPTY)
        return

    username_list = "\n".join(_RELATION_POINT.format(number=num, username=username) for num, username in usernames)

    update.message.reply_text(_RELATIONS_DETAILS.format(usernames=username_list))


def get_user_details(user: TelegramUser) -> str:
    return _DETAILS.format(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
    )


user_commands = [
    CommandHandler("start", handle_start),
    CommandHandler("me", handle_me),
    CommandHandler("relations", handle_relations),
]

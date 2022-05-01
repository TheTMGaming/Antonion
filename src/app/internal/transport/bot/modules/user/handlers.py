from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from app.internal.models.user import TelegramUser
from app.internal.services.bank.account import get_bank_accounts
from app.internal.services.bank.card import get_cards
from app.internal.services.user import get_relations, get_user, try_add_or_update_user
from app.internal.transport.bot.decorators import if_phone_is_set, if_update_message_exist, if_user_exist

_WELCOME = 'Привет, дорогой {username}. Рад приветствовать в "Банке мечты"!'
_UPDATING_DETAILS = "Всё пучком! Я обновил информацию о вас"
_DETAILS = (
    "ID: {id}\n"
    "Ник: {username}\n"
    "Фамилия: {last_name}\n"
    "Имя: {first_name}\n"
    "Телефон: {phone}\n"
    "Счета:\n\t\t\t{bank_accounts}\n"
    "Карты:\n\t\t\t{cards}\n"
)

_RELATIONS_DETAILS = "Вот с этими людьми вы взаимодействовали:\n\n{usernames}"
_RELATION_POINT = "{number}) {username}"


@if_update_message_exist
def handle_start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user

    was_added = try_add_or_update_user(user)

    message = _WELCOME.format(username=user.username) if was_added else _UPDATING_DETAILS

    update.message.reply_text(message)


@if_update_message_exist
@if_user_exist
@if_phone_is_set
def handle_me(update: Update, context: CallbackContext) -> None:
    user = get_user(update.effective_user.id)

    message = get_user_details(user)

    update.message.reply_text(message)


@if_update_message_exist
@if_user_exist
@if_phone_is_set
def handle_relations(update: Update, context: CallbackContext) -> None:
    usernames = enumerate(get_relations(update.effective_user.id), start=1)

    username_list = "\n".join(_RELATION_POINT.format(number=num, username=username) for num, username in usernames)

    update.message.reply_text(_RELATIONS_DETAILS.format(usernames=username_list))


def get_user_details(user: TelegramUser) -> str:
    bank_accounts, cards = get_bank_accounts(user), get_cards(user)

    return _DETAILS.format(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        bank_accounts="\n\t\t\t".join(map(str, bank_accounts)),
        cards="\n\t\t\t".join(map(str, cards)),
    )


user_commands = [
    CommandHandler("start", handle_start),
    CommandHandler("me", handle_me),
    CommandHandler("relations", handle_relations),
]

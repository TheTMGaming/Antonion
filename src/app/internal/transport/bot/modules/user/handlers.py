from telegram import Update
from telegram.ext import CallbackContext

from app.internal.models.user import TelegramUser
from app.internal.services.bank.account import get_bank_accounts
from app.internal.services.bank.card import get_cards
from app.internal.services.user import exists_user, get_user, try_add_user, try_set_phone
from app.internal.transport.bot.modules.user.decorators import if_phone_is_set

_WELCOME = 'Привет, дорогой {username}. Рад приветствовать в "Банке мечты"!'
_UPDATING_DETAILS = "Всё пучком! Я обновил информацию о вас"
_UNKNOWN_USER = "Моя вас не знать. Моя предложить знакомиться с вами! (команда /start)"
_DETAILS = (
    "ID: {id}\n"
    "Ник: {username}\n"
    "Фамилия: {last_name}\n"
    "Имя: {first_name}\n"
    "Телефон: {phone}\n"
    "Счета:\n\t\t\t{bank_accounts}\n"
    "Карты:\n\t\t\t{cards}\n"
)

_UPDATING_PHONE = "Телефон обновил! Готовьтесь к захватывающему спаму!"
_INVALID_PHONE = "Я не могу сохранить эти кракозябры. Проверьте их, пожалуйста!"


def handle_start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user

    was_added = try_add_user(user)

    message = _WELCOME.format(username=user.username) if was_added else _UPDATING_DETAILS

    update.message.reply_text(message)


def handle_set_phone(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    phone = "".join(context.args)

    if not exists_user(user.id):
        update.message.reply_text(_UNKNOWN_USER)
        return

    was_set = try_set_phone(user.id, phone)

    message = _UPDATING_PHONE if was_set else _INVALID_PHONE

    update.message.reply_text(message)


@if_phone_is_set
def handle_me(update: Update, context: CallbackContext) -> None:
    user = get_user(update.effective_user.id)

    message = get_user_details(user)

    update.message.reply_text(message)


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

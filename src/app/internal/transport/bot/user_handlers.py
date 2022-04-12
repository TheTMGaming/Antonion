from telegram import Update
from telegram.ext import CallbackContext

from app.internal.models.user import TelegramUser
from app.internal.services.bank import get_bank_accounts, get_cards
from app.internal.services.user import exists, exists_friend, get_friends, get_user_info, try_add_user, try_set_phone

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

_UNDEFINED_PHONE = "Вы забыли уведомить нас о вашей мобилке. Пожалуйста, продиктуйте! (команда /set_phone)"
_UPDATING_PHONE = "Телефон обновил! Готовьтесь к захватывающему спаму!"
_INVALID_PHONE = "Я не могу сохранить эти кракозябры. Проверьте их, пожалуйста!"

_FRIEND_IDENTIFIER_ERROR = "Такого страдальца я не знаю. Проверьте введённый username/id!"
_FRIEND_ALREADY_EXIST_ERROR = "Так он уже твой друг! Смысл было меня отвлекать от важных дел!"
_FRIEND_ADD_SUCCESS = "Ураа! Да прибудет денюж... в смысле дружба!"
_FRIEND_REMOVE_SUCCESS = "Товарищ покинул ваш чат..."
_FRIEND_LIST_EMPTY = "У вас пока что нет друзей:("
_FRIEND_STUPID_USER = "Друзей совсем нет? Это же ваш профиль!"


def handle_start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user

    was_added = try_add_user(user)

    message = _WELCOME.format(username=user.username) if was_added else _UPDATING_DETAILS
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def handle_set_phone(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    phone = "".join(context.args)

    if not exists(user.id):
        context.bot.send_message(chat_id=update.effective_chat.id, text=_UNKNOWN_USER)
        return

    was_set = try_set_phone(user.id, phone)

    message = _UPDATING_PHONE if was_set else _INVALID_PHONE
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def handle_me(update: Update, context: CallbackContext) -> None:
    user = get_user_info(update.effective_user.id)

    if not user:
        context.bot.send_message(chat_id=update.effective_chat.id, text=_UNKNOWN_USER)
        return

    details = _build_details(user)

    message = details if user.phone else _UNDEFINED_PHONE
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def handle_add_friend(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id

    user = get_user_info(update.effective_user.id)
    friend_identifier = "".join(context.args)

    friend = get_user_info(friend_identifier)

    if user == friend:
        context.bot.send_message(chat_id=chat_id, text=_FRIEND_STUPID_USER)
        return

    if not friend:
        context.bot.send_message(chat_id=chat_id, text=_FRIEND_IDENTIFIER_ERROR)
        return

    if exists_friend(user, friend):
        context.bot.send_message(chat_id=chat_id, text=_FRIEND_ALREADY_EXIST_ERROR)
        return

    user.friends.add(friend)
    context.bot.send_message(chat_id=chat_id, text=_FRIEND_ADD_SUCCESS)


def handle_remove_friend(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id

    user = get_user_info(update.effective_user.id)
    friend_identifier = "".join(context.args)

    friend = get_user_info(friend_identifier)
    if not friend:
        context.bot.send_message(chat_id=chat_id, text=_FRIEND_IDENTIFIER_ERROR)
        return

    user.friends.remove(friend)
    context.bot.send_message(chat_id=chat_id, text=_FRIEND_REMOVE_SUCCESS)


def handle_friends(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user = get_user_info(update.effective_user.id)

    friends = get_friends(user)
    if len(friends) == 0:
        context.bot.send_message(chat_id=chat_id, text=_FRIEND_LIST_EMPTY)
        return

    for details in (_build_details(friend) for friend in friends):
        context.bot.send_message(chat_id=chat_id, text=details)


def _build_details(user: TelegramUser) -> str:
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

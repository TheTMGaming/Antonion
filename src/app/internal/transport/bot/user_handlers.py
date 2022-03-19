from telegram import Update
from telegram.ext import CallbackContext

from app.internal.services.telegram_user import exists, get_user_info, try_add_user, try_set_phone

_WELCOME = 'Привет, дорогой {username}. Рад приветствовать в "Банке мечты"!'
_UPDATING_DETAILS = "Всё пучком! Я обновил информацию о вас"
_UNKNOWN_USER = "Моя вас не знать. Моя предложить знакомиться с вами! (команда /start)"
_DETAILS = (
    "Ловите информацию о вас:\n\n"
    "ID: {id}\n"
    "Ник: {username}\n"
    "Фамилия: {last_name}\n"
    "Имя: {first_name}\n"
    "Телефон: {phone}\n"
)
_UNDEFINED_PHONE = "Вы забыли уведомить нас о вашей мобилке. Пожалуйста, продиктуйте! (команда /set_phone)"
_UPDATING_PHONE = "Телефон обновил! Готовьтесь к захватывающему спаму!"
_INVALID_PHONE = "Я не могу сохранить эти кракозябры. Проверьте их, пожалуйста!"


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

    details = _DETAILS.format(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
    )

    message = details if user.phone else _UNDEFINED_PHONE
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

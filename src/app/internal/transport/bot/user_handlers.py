from telegram import Update
from telegram.ext import CallbackContext

from app.internal.services.user_service import exists, get_user_info, try_add_user, try_set_phone

_WELCOME = "Hello, {username}"
_UPDATING_DETAILS = "Your details have been updated"
_UNKNOWN_USER = "I don't know you yet. Let's get acquainted? (command: /start)"
_DETAILS = (
    "Catch your details:\n\n"
    "ID: {id}\n"
    "Username: {username}\n"
    "First name: {first_name}\n"
    "Last name: {last_name}\n"
    "Phone: {phone}\n"
    "Bot: {is_bot}"
)
_UNDEFINED_PHONE = (
    "Oops. I can't find your phone number in my address book. " "Please write it to me (command: /set_phone [value])"
)
_UPDATING_PHONE = "Your phone has been updated"
_INVALID_PHONE_INPUT = "You entered the wrong phone number"


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

    message = _UPDATING_PHONE if was_set else _INVALID_PHONE_INPUT
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
        is_bot=user.is_bot,
    )

    message = details if user.phone else _UNDEFINED_PHONE
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

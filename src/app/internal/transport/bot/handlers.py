from app.internal.services.user_service import *

from telegram import Update
from telegram.ext import CallbackContext


def handle_start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    adding_message = f"Hello, {user.username}"
    updating_message = f"Your details have been updated"

    was_added = try_add_user(user)

    message = adding_message if was_added else updating_message
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def handle_set_phone(update: Update, context: CallbackContext) -> None:
    user = update.effective_user

    if len(context.args) != 1:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'Expected 1 argument, but was {len(context.args)}')
        return
    phone = context.args[0]

    if not exists(user.id):
        handle_start(update, context)

    updating_message = "Your phone has been updated"
    error_message = "Invalid phone format!!!"

    was_set = try_set_phone(user.id, phone)

    message = updating_message if was_set else error_message
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def handle_me(update: Update, context: CallbackContext) -> None:
    user = get_user_info(update.effective_user.id)
    if not user:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="I don't know you yet. Let's get acquainted? (command: /start)")
        return

    no_phone_message = "Oops. I can't find your phone number in my address book. " \
                       "Please write it to me (command: /set_phone [value])"

    info_message = f"Catch your details:\n\n" \
                   f"ID: {user.id}\n" \
                   f"Username: {user.username}\n" \
                   f"First name: {user.first_name}\n" \
                   f"Last name: {user.last_name}\n" \
                   f"Phone: {user.phone}\n" \
                   f"Bot: {user.is_bot}"

    message = info_message if user.phone else no_phone_message
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

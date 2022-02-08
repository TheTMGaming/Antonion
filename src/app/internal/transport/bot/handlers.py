from telegram import Update
from telegram.ext import CallbackContext
from app.internal.services.user_service import *


def handle_start(update: Update, context: CallbackContext):
    user = update.effective_user
    adding_message = f"Hello, {user.username}"
    updating_message = f"Your details have been updated"

    was_added = try_add_user(user.id, user.username, user.first_name, user.last_name, user.is_bot)

    message = adding_message if was_added else updating_message
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def handle_set_phone(update: Update, context: CallbackContext):
    user = update.effective_user
    phone = context.args[0]

    if not exists(user.id):
        handle_start(update, context)

    updating_message = "Your phone has been updated"
    error_message = "Invalid phone format!!!"

    was_set = try_set_phone(user.id, phone)

    message = updating_message if was_set else error_message
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def handle_me(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    info = get_user_info(user_id)

    no_info_message = r"I don't know you yet. Let's get acquainted? (command: /start)"
    no_phone_message = r"Oops. I can't find your phone number in my address book. " \
                       r"Please write me it (command: /set_phone [value])"
    info_message = "Catch JSON:\n\n" + info.serialize()

    message = no_info_message if not info else no_phone_message if not info.phone else info_message
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

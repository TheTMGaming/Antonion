from telegram.ext import CommandHandler

from app.internal.transport.bot import (
    handle_add_friend,
    handle_friends,
    handle_me,
    handle_remove_friend,
    handle_set_phone,
    handle_start,
)

commands = [
    CommandHandler("start", handle_start),
    CommandHandler("set_phone", handle_set_phone),
    CommandHandler("me", handle_me),
    CommandHandler("friends", handle_friends),
    CommandHandler("add_friend", handle_add_friend),
    CommandHandler("rm_friend", handle_remove_friend),
]

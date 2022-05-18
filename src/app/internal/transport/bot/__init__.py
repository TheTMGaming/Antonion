from app.internal.transport.bot.modules.balance import balance_conversation
from app.internal.transport.bot.modules.friends import (
    accept_conversation,
    add_friend_conversation,
    friends_commands,
    reject_conversation,
    rm_friend_conversation,
)
from app.internal.transport.bot.modules.history import history_conversation
from app.internal.transport.bot.modules.transfer import transfer_conversation
from app.internal.transport.bot.modules.user import password_conversation, phone_conversation, user_commands

commands = [
    *user_commands,
    *friends_commands,
]

conversations = [
    password_conversation,
    balance_conversation,
    transfer_conversation,
    history_conversation,
    phone_conversation,
    add_friend_conversation,
    rm_friend_conversation,
    accept_conversation,
    reject_conversation,
]

handlers = commands + conversations

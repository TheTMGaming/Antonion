from app.internal.bank.presentation.handlers.bot.balance import balance_conversation
from app.internal.bank.presentation.handlers.bot.commands import bank_commands
from app.internal.bank.presentation.handlers.bot.history import history_conversation
from app.internal.bank.presentation.handlers.bot.transfer import transfer_conversation
from app.internal.user.presentation.handlers.bot.commands import user_commands
from app.internal.user.presentation.handlers.bot.friends import (
    accept_conversation,
    add_friend_conversation,
    friends_commands,
    reject_conversation,
    rm_friend_conversation,
)
from app.internal.user.presentation.handlers.bot.password import password_conversation
from app.internal.user.presentation.handlers.bot.phone import phone_conversation

commands = [*user_commands, *friends_commands, *bank_commands]

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

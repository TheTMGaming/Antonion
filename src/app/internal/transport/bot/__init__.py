from app.internal.transport.bot.modules.balance import balance_conversation
from app.internal.transport.bot.modules.friends import add_friend_conversation, friends_commands, rm_friend_conversation
from app.internal.transport.bot.modules.history import history_conversation
from app.internal.transport.bot.modules.transfer import transfer_conversation
from app.internal.transport.bot.modules.user import phone_conversation, user_commands

commands = [
    *user_commands,
    *friends_commands,
]

conversations = [
    balance_conversation,
    transfer_conversation,
    history_conversation,
    phone_conversation,
    add_friend_conversation,
    rm_friend_conversation,
]

handlers = commands + conversations

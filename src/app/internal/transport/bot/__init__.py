from app.internal.transport.bot.modules.balance import balance_conversation
from app.internal.transport.bot.modules.friends import friends_commands
from app.internal.transport.bot.modules.history import history_conversation
from app.internal.transport.bot.modules.transfer import transfer_conversation
from app.internal.transport.bot.modules.user import phone_conversation, user_commands

handlers = [
    *user_commands,
    *friends_commands,
    balance_conversation,
    transfer_conversation,
    history_conversation,
    phone_conversation,
]

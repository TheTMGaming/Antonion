from app.internal.transport.bot.modules.balance import balance_conversation
from app.internal.transport.bot.modules.friends import friends_commands
from app.internal.transport.bot.modules.transfer import transfer_conversation
from app.internal.transport.bot.modules.user import user_commands

handlers = [*user_commands, *friends_commands, balance_conversation, transfer_conversation]

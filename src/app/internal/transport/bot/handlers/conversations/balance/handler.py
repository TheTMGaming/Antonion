from telegram.ext import CommandHandler, ConversationHandler, MessageHandler

from app.internal.transport.bot.handlers.conversations.cancel import cancel
from app.internal.transport.bot.handlers.conversations.filters import INT
from app.internal.transport.bot.modules.balance import BalanceStates, handle_balance_choice, handle_balance_start

balance = ConversationHandler(
    entry_points=[CommandHandler("balance", handle_balance_start)],
    states={
        BalanceStates.CHOICE: [MessageHandler(INT, handle_balance_choice)],
    },
    fallbacks=[cancel],
)

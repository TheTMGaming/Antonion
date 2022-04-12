from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler

from app.internal.transport.bot.balance import handle_balance_choice, handle_balance_start
from app.internal.transport.bot.balance.BalanceStates import BalanceStates
from app.internal.transport.bot.transfer import (
    TransferStates,
    handle_transfer,
    handle_transfer_accrual,
    handle_transfer_destination,
    handle_transfer_destination_document,
    handle_transfer_source_document,
    handle_transfer_start,
)
from app.internal.transport.general_handlers import handle_cancel

_INT_FILTER = Filters.regex("^[0-9]+$")
_DECIMAL_FILTER = Filters.regex("^[0-9]*[.]?[0-9]+(?:[eE][-+]?[0-9]+)?$")

_cancel = CommandHandler("cancel", handle_cancel)

_transfer = ConversationHandler(
    entry_points=[CommandHandler("transfer", handle_transfer_start)],
    states={
        TransferStates.DESTINATION: [MessageHandler(_INT_FILTER, handle_transfer_destination)],
        TransferStates.DESTINATION_DOCUMENT: [MessageHandler(_INT_FILTER, handle_transfer_destination_document)],
        TransferStates.SOURCE_DOCUMENT: [MessageHandler(_INT_FILTER, handle_transfer_source_document)],
        TransferStates.ACCRUAL: [MessageHandler(_DECIMAL_FILTER, handle_transfer_accrual)],
        TransferStates.CONFIRM: [CommandHandler("confirm", handle_transfer)],
    },
    fallbacks=[_cancel],
)

_balance = ConversationHandler(
    entry_points=[CommandHandler("balance", handle_balance_start)],
    states={
        BalanceStates.CHOICE: [MessageHandler(_INT_FILTER, handle_balance_choice)],
    },
    fallbacks=[_cancel],
)

conversations = [_transfer, _balance]

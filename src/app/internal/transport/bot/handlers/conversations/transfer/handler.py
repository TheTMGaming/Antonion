from telegram.ext import CommandHandler, ConversationHandler, MessageHandler

from app.internal.transport.bot.handlers.conversations.cancel import cancel
from app.internal.transport.bot.handlers.conversations.filters import FLOATING, INT
from app.internal.transport.bot.modules.transfer import (
    TransferStates,
    handle_transfer,
    handle_transfer_accrual,
    handle_transfer_destination,
    handle_transfer_destination_document,
    handle_transfer_source_document,
    handle_transfer_start,
)

transfer = ConversationHandler(
    entry_points=[CommandHandler("transfer", handle_transfer_start)],
    states={
        TransferStates.DESTINATION: [MessageHandler(INT, handle_transfer_destination)],
        TransferStates.DESTINATION_DOCUMENT: [MessageHandler(INT, handle_transfer_destination_document)],
        TransferStates.SOURCE_DOCUMENT: [MessageHandler(INT, handle_transfer_source_document)],
        TransferStates.ACCRUAL: [MessageHandler(FLOATING, handle_transfer_accrual)],
        TransferStates.CONFIRM: [CommandHandler("confirm", handle_transfer)],
    },
    fallbacks=[cancel],
)

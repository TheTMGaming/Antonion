from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler

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

_cancel = CommandHandler("cancel", handle_cancel)

_transfer_account = ConversationHandler(
    entry_points=[CommandHandler("transfer", handle_transfer_start)],
    states={
        TransferStates.DESTINATION: [MessageHandler(Filters.regex("^[0-9]+$"), handle_transfer_destination)],
        TransferStates.DESTINATION_DOCUMENT: [
            MessageHandler(Filters.regex("^[0-9]+$"), handle_transfer_destination_document)
        ],
        TransferStates.SOURCE_DOCUMENT: [MessageHandler(Filters.regex("^[0-9]+$"), handle_transfer_source_document)],
        TransferStates.ACCRUAL: [
            MessageHandler(Filters.regex("^[0-9]*[.]?[0-9]+(?:[eE][-+]?[0-9]+)?$"), handle_transfer_accrual)
        ],
        TransferStates.CONFIRM: [CommandHandler("confirm", handle_transfer)],
    },
    fallbacks=[_cancel],
)

conversations = [
    _transfer_account,
]

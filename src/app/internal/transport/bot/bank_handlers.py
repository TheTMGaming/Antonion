from typing import Callable, Union

from telegram import Bot, Update
from telegram.ext import CallbackContext

from app.internal.models.bank import BankAccount, BankCard
from app.internal.services.bank import (
    confirm_bank_account,
    confirm_card,
    get_bank_account,
    get_card,
    validate_bank_account_number,
    validate_card_number,
)

_UNKNOWN_CARD = "Такая карта не зарегистрирована в нашем замечательном банке"
_BALANCE_BY_CARD = "На карточке {card_number} лежит {balance}"
_CONFIRMATION_CARD_ERROR = "Это не ваша карта, либо вы решили взломать Василия!"

_UNKNOWN_BANK_ACCOUNT = (
    "Такого счёта нет. Наверное, вы забыли позвонить Василию, чтобы он создал для вас банковский счёт!"
)
_BALANCE_BY_BANK_ACCOUNT = "На счёте {account_number} лежит {balance}"
_CONFIRMATION_BANK_ACCOUNT_ERROR = "Неее, это не ваш счёт..."

_INVALID_INPUT_MESSAGE = "Проверьте правильность введённых данных!"


def handle_getting_balance_by_card(update: Update, context: CallbackContext) -> None:
    number = "".join(context.args)
    if not validate_card_number(number):
        context.bot.send_message(chat_id=update.effective_chat.id, text=_INVALID_INPUT_MESSAGE)
        return

    card = get_card(number)

    _send_balance_details(
        update=update,
        bot=context.bot,
        document=card,
        confirm=confirm_card,
        unknown_document_error=_UNKNOWN_CARD,
        confirmation_error=_CONFIRMATION_CARD_ERROR,
        get_balance_details=lambda card_: _BALANCE_BY_CARD.format(
            card_number=card_.number, balance=card_.bank_account.balance
        ),
    )


def handle_getting_balance_by_account(update: Update, context: CallbackContext) -> None:
    number = "".join(context.args)
    if not validate_bank_account_number(number):
        context.bot.send_message(chat_id=update.effective_chat.id, text=_INVALID_INPUT_MESSAGE)
        return

    bank_account = get_bank_account(number)

    _send_balance_details(
        update=update,
        bot=context.bot,
        document=bank_account,
        confirm=confirm_bank_account,
        unknown_document_error=_UNKNOWN_BANK_ACCOUNT,
        confirmation_error=_CONFIRMATION_BANK_ACCOUNT_ERROR,
        get_balance_details=lambda account: _BALANCE_BY_BANK_ACCOUNT.format(
            account_number=account.number, balance=account.balance
        ),
    )


def _send_balance_details(
    update: Update,
    bot: Bot,
    document: Union[BankCard, BankAccount],
    confirm: Callable,
    unknown_document_error: str,
    confirmation_error: str,
    get_balance_details: Callable,
) -> None:
    chat_id = update.effective_chat.id

    if not document:
        bot.send_message(chat_id=chat_id, text=unknown_document_error)
        return

    if not confirm(document, update.effective_user.id):
        bot.send_message(chat_id=chat_id, text=confirmation_error)
        return

    bot.send_message(chat_id=chat_id, text=get_balance_details(document))

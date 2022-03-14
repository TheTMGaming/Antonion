from typing import Callable, Union

from telegram import Bot, Update
from telegram.ext import CallbackContext, ConversationHandler

from app.internal.models.bank import BankAccount, BankCard, Passport
from app.internal.services.bank import get_bank_account, get_card
from app.internal.services.bank.confirmations import BankAccountConfirmation, BankCardConfirmation, DocumentConfirmation

from .BalanceOperationStates import BalanceOperationStates

_INCORRECT_CARD_NUMBER = "Я не понимать ваша номер карта O_o. В номере можно использовать только цифры и пробелы!"
_UNKNOWN_CARD_NUMBER = (
    "Такой карточки в записной книжке у меня нет. Просьба: позвоните Васе, чтобы он записал вас на приём к моей тёте"
)
_ASK_CODE = "Введите cvv2/cvc2-код"
_BALANCE_BY_CARD = "На карточке '{card_number}' лежит '{balance}' бананов"
_REPEAT_OPERATION_BY_CARD = "Неправильный номер карты или код. Начините сначала"

_INCORRECT_BANK_ACCOUNT_NUMBER = (
    "Кажется, вы ввели неправильно номер счёта, либо просто забыли..."
    "В номере можно использовать только цифры и пробелы!"
)
_ASK_PASSPORT = "Введите серию и номер паспорта через пробел, а то я глупы... впрочем, неважно"
_REPEAT_OPERATION_BY_BANK_ACCOUNT = "Неправильный номер счёта или идентификатор паспорта. Начините сначала"
_BALANCE_BY_BANK_ACCOUNT = "На счёте '{account_number}' лежит '{balance}' бананов"

_EXPECTED_PASSPORT_ARGS = (
    "Я ожидал серию и номер паспорта через пробел, но получил это... Введите ещё раз, только как я хочу!"
)

_SESSION_CARD_NUMBER = "card_number"
_SESSION_BANK_ACCOUNT_NUMBER = "bank_account_number"


def handle_getting_balance_by_card(update: Update, context: CallbackContext) -> int:
    return _save_document_number_to_session(
        chat_id=update.effective_chat.id,
        context=context,
        session_number_field=_SESSION_CARD_NUMBER,
        incorrect_number_message=_INCORRECT_CARD_NUMBER,
        next_question_message=_ASK_CODE,
    )


def handle_confirmation_card(update: Update, context: CallbackContext) -> int:
    code = update.message.text
    card = get_card(context.user_data[_SESSION_CARD_NUMBER])

    return _send_balance_details(
        chat_id=update.effective_chat.id,
        bot=context.bot,
        document=card,
        confirmation=BankCardConfirmation(card, code),
        confirmation_error_message=_REPEAT_OPERATION_BY_CARD,
        get_message_with_balance=lambda card_: _BALANCE_BY_CARD.format(
            card_number=card_.number, balance=card_.bank_account.balance
        ),
    )


def handle_getting_balance_by_account(update: Update, context: CallbackContext) -> int:
    return _save_document_number_to_session(
        chat_id=update.effective_chat.id,
        context=context,
        session_number_field=_SESSION_BANK_ACCOUNT_NUMBER,
        incorrect_number_message=_INCORRECT_BANK_ACCOUNT_NUMBER,
        next_question_message=_ASK_PASSPORT,
    )


def handle_confirmation_account(update: Update, context: CallbackContext) -> int:
    chat_id = update.effective_chat.id

    passport_args = update.message.text.split()
    if len(passport_args) != Passport.IDENTIFIERS_NUMBER or not all(map(str.isdigit, passport_args)):
        context.bot.send_message(chat_id=chat_id, text=_EXPECTED_PASSPORT_ARGS)
        return BalanceOperationStates.CONFIRMATION

    series, number = passport_args
    bank_account = get_bank_account(context.user_data[_SESSION_BANK_ACCOUNT_NUMBER])

    return _send_balance_details(
        chat_id=chat_id,
        bot=context.bot,
        document=bank_account,
        confirmation=BankAccountConfirmation(bank_account, series, number),
        confirmation_error_message=_REPEAT_OPERATION_BY_BANK_ACCOUNT,
        get_message_with_balance=lambda account: _BALANCE_BY_BANK_ACCOUNT.format(
            account_number=account.number, balance=account.balance
        ),
    )


def _save_document_number_to_session(
    chat_id: int,
    context: CallbackContext,
    session_number_field: str,
    incorrect_number_message: str,
    next_question_message: str,
) -> int:
    number = "".join(context.args)
    if not number.isdigit():
        context.bot.send_message(chat_id=chat_id, text=incorrect_number_message)
        return ConversationHandler.END

    context.user_data[session_number_field] = number

    context.bot.send_message(chat_id=chat_id, text=next_question_message)
    return BalanceOperationStates.CONFIRMATION


def _send_balance_details(
    chat_id: int,
    bot: Bot,
    document: Union[BankCard, BankAccount],
    confirmation: DocumentConfirmation,
    confirmation_error_message: str,
    get_message_with_balance: Callable,
) -> int:
    if not document or not confirmation.confirm():
        bot.send_message(chat_id=chat_id, text=confirmation_error_message)
        return ConversationHandler.END

    bot.send_message(chat_id=chat_id, text=get_message_with_balance(document))
    return ConversationHandler.END

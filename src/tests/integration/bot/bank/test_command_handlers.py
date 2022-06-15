import pytest
from django.core.files.base import ContentFile
from telegram import PhotoSize, Update
from telegram.ext import CallbackContext

from app.internal.bank.db.models import BankAccount, Transaction
from app.internal.bank.presentation.handlers.bot.commands import (
    _LAST_END_MESSAGE,
    _NEW_TRANSACTIONS_EMPTY_MESSAGE,
    handle_last,
)
from app.internal.user.db.models import TelegramUser


@pytest.mark.django_db
@pytest.mark.integration
def test_last__empty(update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser) -> None:
    handle_last(update, context)

    update.message.reply_text.assert_called_once_with(_NEW_TRANSACTIONS_EMPTY_MESSAGE)


@pytest.mark.django_db
@pytest.mark.integration
def test_last(
    update: Update,
    context: CallbackContext,
    telegram_user_with_phone: TelegramUser,
    bank_account: BankAccount,
    another_account: BankAccount,
    photo: PhotoSize,
) -> None:
    for with_photo in [True, False]:
        update.reset_mock()
        transactions = Transaction.objects.bulk_create(
            [
                Transaction(
                    source=bank_account,
                    destination=another_account,
                    accrual=10,
                    photo=ContentFile(content=photo.get_file().download_as_bytearray(), name=str(i))
                    if with_photo
                    else None,
                )
                for i in range(2)
            ]
            + [
                Transaction(
                    source=another_account,
                    destination=bank_account,
                    accrual=10,
                    photo=ContentFile(content=photo.get_file().download_as_bytearray(), name=str(i + 100))
                    if with_photo
                    else None,
                )
                for i in range(2)
            ]
        )

        handle_last(update, context)
        for transaction in transactions:
            transaction.photo.delete(save=False)

        if with_photo:
            assert update.message.reply_photo.call_count == len(transactions)
            update.message.reply_text.assert_called_once_with(_LAST_END_MESSAGE)
        else:
            assert update.message.reply_text.call_count == len(transactions) + 1
            update.message.reply_text.assert_called_with(_LAST_END_MESSAGE)

        for transaction in transactions:
            transaction.refresh_from_db()
            assert transaction.was_source_viewed is (transaction.source.owner == telegram_user_with_phone)
            assert transaction.was_destination_viewed is (transaction.destination.owner == telegram_user_with_phone)

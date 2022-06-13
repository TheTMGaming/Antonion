from typing import Iterable

from django.conf import settings

from app.internal.bank.db.models import BankAccount, Transaction
from app.internal.utils.OperationNames import OperationNames
from app.internal.utils.Table import Table


def build_transfer_history(account: BankAccount, transactions: Iterable[Transaction]) -> str:
    history = Table()
    history.field_names = ["Дата", "Тип операции", "Отправитель/Получатель", "Сумма операции", "Картинка"]

    for transaction in transactions:
        is_accrual = transaction.destination == account

        time = transaction.created_at.strftime(settings.DATETIME_PARSE_FORMAT)
        type_ = (OperationNames.ACCRUAL if is_accrual else OperationNames.DEBIT).value
        username = (transaction.source if is_accrual else transaction.destination).get_owner().username
        photo_url = transaction.photo.url if transaction.photo else "Нет"

        history.add_row([time, type_, username, transaction.accrual, photo_url])

    return history.get_string()

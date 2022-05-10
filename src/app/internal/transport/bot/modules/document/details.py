from typing import Dict, Type

from telegram import Update

from app.internal.models.bank import BankAccount, BankCard, BankObject

_DOCUMENT_GROUPS = "Счета:\n{accounts}\nКарты:\n{cards}\n"
_DOCUMENT_VARIANT = "{number}) {document}"
_DOCUMENT_VARIANT_WITH_BALANCE = "{number}) {document} ({balance})"


def send_document_list(update: Update, documents: Dict[int, BankObject], welcome_text: str, show_balance=False) -> None:
    methods = _DOCUMENT_GROUPS.format(
        accounts=build_details(documents, BankAccount, show_balance),
        cards=build_details(documents, BankCard, show_balance),
    )

    update.message.reply_text(welcome_text + methods)


def build_details(
    documents: Dict[int, BankObject], type_document: Type[BankCard | BankAccount], show_balance=False
) -> str:
    pattern = _DOCUMENT_VARIANT_WITH_BALANCE if show_balance else _DOCUMENT_VARIANT
    return "\t" * 3 + "\n\t\t\t".join(
        pattern.format(
            number=num,
            document=document.short_number,
            balance=document.get_balance(),
        )
        for num, document in documents.items()
        if isinstance(document, type_document)
    )

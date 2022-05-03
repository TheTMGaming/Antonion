from typing import Tuple

from app.internal.models.bank import BankCard, BankAccount
from app.internal.models.user import TelegramUser


def get_documents(user: TelegramUser) -> Tuple[Tuple[BankAccount], Tuple[BankCard]]:
    cards: Tuple[BankCard] = tuple(BankCard.objects.select_related("bank_account").filter(bank_account__owner=user))
    accounts: Tuple[BankAccount] = tuple(set(card.bank_account for card in cards))

    return accounts, cards

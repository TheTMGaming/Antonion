from typing import List

from app.internal.models.bank import BankCard
from app.internal.models.user import TelegramUser
from app.internal.services.bank.account import get_bank_accounts


def get_card(number: str) -> BankCard:
    return BankCard.objects.filter(number=number).first()


def get_cards(user: TelegramUser) -> List[BankCard]:
    return list(card for account in get_bank_accounts(user) for card in account.bank_cards.all())

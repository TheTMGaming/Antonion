import logging
from decimal import Decimal
from itertools import chain
from typing import List
from unittest.mock import MagicMock

import pytest
from django.conf import settings
from django.db.models import QuerySet
from ninja import UploadedFile
from telegram import User

from app.internal.bank.db.models import BankAccount, BankCard
from app.internal.user.db.models import FriendRequest, SecretKey, TelegramUser
from app.internal.user.db.repositories import SecretKeyRepository, TelegramUserRepository

BALANCE = Decimal(10**4)
PASSWORD = "1337<PrO>228"
WRONG_PASSWORD = "0>Spyric<0"
PHONE = "+78005553535"
KEY = "noob"
WRONG_KEY = "pro"
TIP = "Who am i?"

CORRECT_PHONE_NUMBERS = list(
    chain(
        *(
            [
                f"{start}8005553535",
                f"{start} (800) 555 35 35",
                f"{start}-(800)-555-35-35",
                f"{start}-800-555-35-35",
                f"{start}800 55 535 35",
            ]
            for start in ["7", "8", "+7"]
        )
    )
)

WRONG_PHONE_NUMBERS = [
    *(f"+{start}8005553535" for start in chain(range(7), [9])),
    *(f"{start}8005553535" for start in chain(range(7), [9])),
    *("1" * length for length in chain(range(11), range(12, 30))),
    *("a" * length for length in chain(range(11), range(12, 30))),
    *("a1" * (length // 2) + "a" * (length % 2) for length in range(30)),
    *("8" * 11 + "a" * amount for amount in range(1, 6)),
    *("8" * 11 + " " + "a" * amount for amount in range(1, 6)),
    *("8" * 11 + " " * amount for amount in range(1, 6)),
    *(" " * amount for amount in range(30)),
    "",
    *(f"{start}.800.55,535,35" for start in ["7", "8", "+7"]),
    "    88005553535",
    "aaa        88005553535",
    "        88005553535",
    "a b 88005553535",
    "88005553535 1 2",
    "8800",
    "aaaaaaaaaaa",
]


user_repo = TelegramUserRepository()
secret_repo = SecretKeyRepository()


def pytest_configure(config):
    logging.disable()


@pytest.fixture(scope="function")
def user(user_id=1337, first_name="Вася", last_name="Пупкин", username="geroj") -> User:
    return User(id=user_id, first_name=first_name, last_name=last_name, username=username, is_bot=False)


@pytest.fixture(scope="function")
def second_user(user_id=228, first_name="Петька", last_name="Ас", username="very_metkij") -> User:
    return User(id=user_id, first_name=first_name, last_name=last_name, username=username, is_bot=False)


@pytest.fixture(scope="function")
def third_user(user_id=1111, first_name="Ваня", last_name="Чоткий", username="very_big_pig") -> User:
    return User(id=user_id, first_name=first_name, last_name=last_name, username=username, is_bot=False)


@pytest.fixture(scope="function")
def users(user, second_user: User, third_user: User) -> List[User]:
    return [user, second_user, third_user]


@pytest.fixture(scope="function")
def telegram_users(users: List[User]) -> List[TelegramUser]:
    return [
        TelegramUser.objects.create(
            id=user.id, username=user.username, first_name=user.first_name, last_name=user.last_name
        )
        for user in users
    ]


@pytest.fixture(scope="function")
def telegram_user(telegram_users: List[TelegramUser]) -> TelegramUser:
    return telegram_users[0]


@pytest.fixture(scope="function")
def another_telegram_user(telegram_users: List[TelegramUser]) -> TelegramUser:
    return telegram_users[1]


@pytest.fixture(scope="function")
def another_telegram_users(telegram_users: List[TelegramUser]) -> List[TelegramUser]:
    return telegram_users[1:]


@pytest.fixture(scope="function")
def telegram_user_with_password(telegram_user_with_phone: TelegramUser) -> TelegramUser:
    telegram_user_with_phone.password = user_repo._hash(PASSWORD)
    telegram_user_with_phone.save(update_fields=["password"])

    secret_repo.create(telegram_user_with_phone.id, KEY, TIP)

    return telegram_user_with_phone


@pytest.fixture(scope="function")
def telegram_user_with_phone(telegram_user: TelegramUser) -> TelegramUser:
    telegram_user.phone = PHONE
    telegram_user.save(update_fields=["phone"])

    return telegram_user


@pytest.fixture(scope="function")
def bank_accounts(telegram_user_with_phone: TelegramUser, amount=3) -> List[BankAccount]:
    return [BankAccount.objects.create(balance=BALANCE, owner=telegram_user_with_phone) for _ in range(amount)]


@pytest.fixture(scope="function")
def bank_account(bank_accounts: List[BankAccount]) -> BankAccount:
    return bank_accounts[0]


@pytest.fixture(scope="function")
def another_account(another_accounts: List[BankAccount]) -> BankAccount:
    return another_accounts[0]


@pytest.fixture(scope="function")
def another_accounts(another_telegram_users: List[TelegramUser], bank_accounts: List[BankAccount]) -> List[BankAccount]:
    accounts = []
    for user in another_telegram_users:
        accounts.append(BankAccount.objects.create(balance=BALANCE, owner=user))

    return accounts


@pytest.fixture(scope="function")
def cards(bank_accounts: List[BankAccount]) -> List[BankCard]:
    return [BankCard.objects.create(bank_account=account) for account in bank_accounts]


@pytest.fixture(scope="function")
def card(cards: List[BankCard]) -> BankCard:
    return cards[0]


@pytest.fixture(scope="function")
def another_card(another_cards: List[BankCard]) -> BankCard:
    return another_cards[0]


@pytest.fixture(scope="function")
def another_cards(another_accounts: List[BankAccount]) -> List[BankCard]:
    cards = []
    for account in another_accounts:
        cards.append(BankCard.objects.create(bank_account=account))

    return cards


@pytest.fixture(scope="function")
def friends(telegram_user: TelegramUser, telegram_users: List[TelegramUser]) -> List[TelegramUser]:
    friends = [friend for friend in telegram_users if friend != telegram_user]

    telegram_user.friends.add(*friends)

    for friend in friends:
        friend.phone = PHONE

    TelegramUser.objects.bulk_update(friends, fields=["phone"])

    return friends


@pytest.fixture(scope="function")
def friend(friends: List[TelegramUser]) -> TelegramUser:
    return friends[0]


@pytest.fixture(scope="function")
def friend_with_account(friend: TelegramUser, friend_account: BankAccount) -> TelegramUser:
    return friend


@pytest.fixture(scope="function")
def friend_accounts(friends: List[TelegramUser]) -> List[BankAccount]:
    return [BankAccount.objects.create(balance=BALANCE, owner=friend) for friend in friends]


@pytest.fixture(scope="function")
def friend_account(friend_accounts: List[BankAccount]) -> BankAccount:
    return friend_accounts[0]


@pytest.fixture(scope="function")
def friend_cards(friend_accounts: List[BankAccount]) -> List[BankCard]:
    return [BankCard.objects.create(bank_account=account) for account in friend_accounts]


@pytest.fixture(scope="function")
def friend_card(friend_cards: List[BankCard]) -> BankCard:
    return friend_cards[0]


@pytest.fixture(scope="function")
def friend_request(telegram_user: TelegramUser, another_telegram_user: TelegramUser) -> FriendRequest:
    return FriendRequest.objects.create(source=another_telegram_user, destination=telegram_user)


@pytest.fixture(scope="function")
def friend_requests(telegram_user: TelegramUser, telegram_users: List[TelegramUser]) -> QuerySet[FriendRequest]:
    return FriendRequest.objects.bulk_create(
        FriendRequest(source=another, destination=telegram_user)
        for another in telegram_users
        if another != telegram_user
    )


@pytest.fixture(scope="function")
def uploaded_image() -> UploadedFile:
    image = MagicMock()

    read = MagicMock()
    read.return_value = b"228"

    image.read = read
    image.content_type = "image/jpg"
    image.size = settings.MAX_SIZE_PHOTO_BYTES - 1

    return image

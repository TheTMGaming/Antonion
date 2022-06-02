from decimal import Decimal
from typing import List

import pytest
from django.db.models import QuerySet
from telegram import User

from app.internal.bank.db.models import BankAccount, BankCard
from app.internal.user.db.models import FriendRequest, SecretKey, TelegramUser
from app.internal.user.db.repositories import TelegramUserRepository

BALANCE = Decimal(10**4)
PASSWORD = "1337<PrO>228"
WRONG_PASSWORD = "0>Spyric<0"
KEY = "noob"
WRONG_KEY = "pro"
TIP = "Who am i?"

user_repo = TelegramUserRepository()


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
def telegram_users_with_phone(telegram_users: List[TelegramUser], phone="+78005553535") -> List[TelegramUser]:
    for user in telegram_users:
        user.phone = phone

    TelegramUser.objects.bulk_update(telegram_users, fields=["phone"])

    return telegram_users


@pytest.fixture(scope="function")
def telegram_users_with_password(telegram_users_with_phone: List[TelegramUser]) -> List[TelegramUser]:
    for user in telegram_users_with_phone:
        user.password = user_repo._hash(PASSWORD)
        SecretKey.objects.create(telegram_user=user, value=KEY, tip=TIP)

    TelegramUser.objects.bulk_update(telegram_users_with_phone, fields=["password"])

    return telegram_users_with_phone


@pytest.fixture(scope="function")
def telegram_user_with_password(telegram_users_with_password: List[TelegramUser]) -> TelegramUser:
    return telegram_users_with_password[0]


@pytest.fixture(scope="function")
def telegram_user_with_phone(telegram_users_with_phone: List[TelegramUser]) -> TelegramUser:
    return telegram_users_with_phone[0]


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
        friend.friends.add(telegram_user)

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

from ninja import Schema
from pydantic import Field


class PhoneIn(Schema):
    phone: str = Field(max_length=63)


class PasswordIn(Schema):
    key: str = Field(max_length=255)
    password: str = Field(max_length=255)


class TelegramUserOut(Schema):
    id: int
    username: str
    first_name: str
    last_name: str
    phone: str

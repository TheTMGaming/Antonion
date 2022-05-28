from ninja import Schema
from pydantic import Field


class TelegramUserIn(Schema):
    username: str = Field(max_length=255)
    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)
    phone: str = Field(regex=r"^\+\d{11}")


class TelegramUserOut(TelegramUserIn):
    id: int

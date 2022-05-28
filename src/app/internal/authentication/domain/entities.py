from ninja import Schema
from pydantic import Field


class CredentialsSchema(Schema):
    username: str = Field(max_length=255)
    password: str = Field(max_length=255)


class AccessTokenOut(Schema):
    access_token: str

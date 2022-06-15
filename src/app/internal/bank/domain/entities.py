from datetime import datetime
from typing import Optional

from ninja import Schema, UploadedFile
from pydantic import Field, validator


class BankAccountOut(Schema):
    number: str
    balance: float


class BankCardOut(Schema):
    number: str
    account: BankAccountOut


class TransactionOut(Schema):
    source: str
    destination: str
    accrual: float
    photo: Optional[str]
    created_at: datetime


class TransferIn(Schema):
    source: int
    destination: int
    accrual: float

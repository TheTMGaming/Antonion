from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from django.apps import apps
from django.conf import settings
from django.utils import timezone
from jwt import PyJWTError, decode, encode

from app.internal.authentication.TokenTypes import TokenTypes

CREATED_AT = "created_at"
TELEGRAM_ID = "telegram_id"
TOKEN_TYPE = "type"
PAYLOAD_FIELDS = [CREATED_AT, TELEGRAM_ID, TOKEN_TYPE]

ALGORITHM = "HS256"


TelegramUser = apps.get_model("app", "TelegramUser", require_ready=True)


def now() -> datetime:
    return timezone.now()


def from_timestamp(value: float) -> datetime:
    return datetime.fromtimestamp(value, tz=timezone.get_current_timezone())


def get_authenticated_telegram_user(payload: Dict[str, Any]) -> Optional[TelegramUser]:
    return TelegramUser.objects.filter(id=payload.get(TELEGRAM_ID)).first()


def generate_token(telegram_id: int, token_type: TokenTypes) -> str:
    payload = {TOKEN_TYPE: token_type.value, TELEGRAM_ID: telegram_id, CREATED_AT: now().timestamp()}

    return encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def is_payload_valid(payload: Dict[str, Any]) -> bool:
    return bool(payload) and Counter(payload.keys()) == Counter(PAYLOAD_FIELDS)


def try_get_payload(token: str) -> Dict[str, Any]:
    try:
        return decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except PyJWTError:
        return {}


def is_token_alive(payload: Dict[str, Any], token_type: TokenTypes, ttl: timedelta) -> bool:
    lifetime = now() - from_timestamp(float(payload[CREATED_AT]))

    return payload.get(TOKEN_TYPE) == token_type.value and lifetime < ttl

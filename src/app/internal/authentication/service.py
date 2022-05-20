from typing import Optional, Tuple

from app.internal.authentication.TokenTypes import TokenTypes
from app.internal.authentication.utils import generate_token
from app.internal.models.user import RefreshToken, TelegramUser


def get_user_by_credentials(username: str, password: str) -> Optional[TelegramUser]:
    return TelegramUser.objects.get_by_credentials(username, password).first()


def get_refresh_token_from_db(value: str) -> Optional[RefreshToken]:
    return RefreshToken.objects.filter(value=value).first()


def create_access_and_refresh_tokens(user: TelegramUser) -> Tuple[str, str]:
    access, refresh = generate_token(user.id, TokenTypes.ACCESS), generate_token(user.id, TokenTypes.REFRESH)

    RefreshToken.objects.get_or_create(telegram_user=user, value=refresh)

    return access, refresh


def update_access_and_refresh_tokens(refresh_token: RefreshToken) -> Optional[Tuple[str, str]]:
    if refresh_token.revoked:
        RefreshToken.objects.filter(telegram_user=refresh_token.telegram_user).update(revoked=True)
        return None

    refresh_token.revoked = True
    refresh_token.save(update_fields=["revoked"])

    return create_access_and_refresh_tokens(refresh_token.telegram_user)

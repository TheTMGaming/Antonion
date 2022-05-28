from typing import Optional

from app.internal.authentication.db.models import RefreshToken
from app.internal.authentication.domain.interfaces import IAuthRepository
from app.internal.user.db.models import TelegramUser


class AuthRepository(IAuthRepository):
    def get_authenticated_telegram_user(self, telegram_id: int) -> Optional[TelegramUser]:
        return TelegramUser.objects.filter(id=telegram_id).first()

    def get_refresh_token_from_db(self, value: str) -> Optional[RefreshToken]:
        return RefreshToken.objects.filter(value=value).first()

    def create_refresh_token(self, user: TelegramUser, value: str) -> None:
        return RefreshToken.objects.get_or_create(telegram_user=user, value=value)

    def revoke_all_refresh_tokens(self, user: TelegramUser) -> None:
        RefreshToken.objects.filter(telegram_user=user).update(revoked=True)

    def revoke_refresh_token(self, token: RefreshToken) -> None:
        token.revoked = True
        token.save(update_fields=["revoked"])

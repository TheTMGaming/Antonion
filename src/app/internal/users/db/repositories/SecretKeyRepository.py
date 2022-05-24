from telegram import User

from app.internal.users.db.models import SecretKey


class SecretKeyRepository:
    def is_secret_key_correct(self, actual: str, user: User) -> bool:
        return SecretKey.objects.check_value(user.id, actual)

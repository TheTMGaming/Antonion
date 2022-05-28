from django.http import HttpRequest

from app.internal.user.domain.entities.user import TelegramUserOut
from app.internal.user.domain.services import TelegramUserService


class TelegramUserHandlers:
    def __init__(self, user_service: TelegramUserService):
        self._user_service = user_service

    def get_about_me(self, request: HttpRequest) -> TelegramUserOut:
        user = self._user_service.get_user(request.telegram_user.id)

        return TelegramUserOut.from_orm(user)

    def update_me(self, request: HttpRequest):
        pass

    def update_phone(self, request: HttpRequest):
        pass

    def update_password(self, request: HttpRequest):
        pass

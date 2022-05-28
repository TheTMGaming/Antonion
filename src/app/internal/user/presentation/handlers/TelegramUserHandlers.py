from django.http import HttpRequest
from ninja import Body

from app.internal.general.exceptions import BadRequestException, IntegrityException
from app.internal.general.responses import SuccessResponse
from app.internal.user.domain.entities.user import TelegramUserOut, PhoneSchema, PasswordSchema
from app.internal.user.domain.services import TelegramUserService


class TelegramUserHandlers:
    def __init__(self, user_service: TelegramUserService):
        self._user_service = user_service

    def get_about_me(self, request: HttpRequest) -> TelegramUserOut:
        user = self._user_service.get_user(request.telegram_user.id)

        return TelegramUserOut.from_orm(user)

    def update_phone(self, request: HttpRequest, body: PhoneSchema = Body(...)) -> PhoneSchema:
        if not self._user_service.try_set_phone(request.telegram_user.id, body.phone):
            raise BadRequestException()

        user = self._user_service.get_user(request.telegram_user.id)

        return PhoneSchema.from_orm(user)

    def update_password(self, request: HttpRequest, body: PasswordSchema = Body(...)) -> SuccessResponse:
        if not self._user_service.is_secret_key_correct(request.telegram_user, body.key):
            raise BadRequestException()

        if not self._user_service.try_update_password(request.telegram_user, body.password):
            raise IntegrityException()

        return SuccessResponse()
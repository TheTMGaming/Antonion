from typing import Optional

from django.http import HttpRequest, JsonResponse
from django.views import View

from app.internal.models.telegram_info import TelegramUser
from app.internal.services.telegram_user import get_user_info


class UserDetailsView(View):
    _SUCCESS_OPERATION = "Success"
    _UNKNOWN_USER = "Unknown user '{user_id}'"
    _UNDEFINED_PHONE = "The user '{user_id}' does not have a phone number"

    def get(self, request: HttpRequest, user_id: int) -> JsonResponse:
        info = get_user_info(user_id)

        data = {
            "message": UserDetailsView._get_message(expected_user_id=user_id, found_info=info),
            "user": info.to_dictionary() if info else {},
        }
        params = {"indent": 2}

        return JsonResponse(data=data, json_dumps_params=params)

    @staticmethod
    def _get_message(expected_user_id: int, found_info: Optional[TelegramUser]) -> str:
        if not found_info:
            return UserDetailsView._UNKNOWN_USER.format(user_id=expected_user_id)

        if not found_info.phone:
            return UserDetailsView._UNDEFINED_PHONE.format(user_id=expected_user_id)

        return UserDetailsView._SUCCESS_OPERATION

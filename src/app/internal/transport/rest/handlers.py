from django.http import HttpRequest, JsonResponse

from app.internal.services.user_service import get_user_info


def handle_me(request: HttpRequest, user_id: int) -> JsonResponse:
    info = get_user_info(user_id)

    success_message = "Success"
    unknown_user_message = f"Unknown user '{user_id}'"
    no_phone_message = f"The user '{user_id}' does not have a phone number"

    message = unknown_user_message if not info else no_phone_message if not info.phone else success_message

    data = {"message": message, "user": info._asdict() if info and info.phone else None}
    parameters = {
        "indent": 2,
    }

    return JsonResponse(data=data, json_dumps_params=parameters)

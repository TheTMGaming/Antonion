from django.http import HttpRequest, JsonResponse

from app.internal.services.user_service import get_user_info


def handle_me(request: HttpRequest, user_id: int) -> JsonResponse:
    info = get_user_info(user_id)

    success_message = f"Success"
    unknown_user_message = f"Unknown user '{user_id}'"
    no_phone_message = f"The user '{user_id}' does not have a phone number"

    message = unknown_user_message if not info else \
        no_phone_message if not info.phone else success_message

    # info._asdict(): it has the underscore only to try and prevent conflicts with possible field names.
    data = {
        'message': message,
        'user': info._asdict() if info and info.phone else None
    }

    return JsonResponse(data=data, json_dumps_params={'indent': 2})

from django.http import JsonResponse
from app.internal.services.user_service import get_user_info


def handle_me(request, user_id):
    info = get_user_info(user_id)

    success_message = f"Success"
    unknown_user_message = f"Unknown user_id '{user_id}'"
    no_phone_message = f"User '{user_id}' does not have a phone number"

    message = unknown_user_message if not info else \
        no_phone_message if not info.phone else success_message

    return JsonResponse({
        'message': message,
        'user': info.__dict__ if info and info.phone else None
    }, json_dumps_params={'indent': 2})

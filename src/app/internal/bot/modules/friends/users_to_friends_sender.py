from telegram import Update
from telegram.ext import CallbackContext

from app.internal.bot.modules.friends.FriendStates import FriendStates
from app.internal.bot.modules.general import mark_conversation_end
from app.internal.user.db.repositories import FriendRequestRepository
from app.internal.user.domain.services import FriendRequestService

_USERNAME_VARIANT = "{num}) {username}"

_request_service = FriendRequestService(request_repo=FriendRequestRepository())


def send_username_list(
    update: Update, context: CallbackContext, list_empty_message: str, usernames_session: str, welcome: str
) -> int:
    usernames = _request_service.get_usernames_to_friends(update.effective_user)

    if not usernames:
        update.message.reply_text(list_empty_message)
        return mark_conversation_end(context)

    username_list = dict((num, username) for num, username in enumerate(usernames, start=1))
    context.user_data[usernames_session] = username_list

    update.message.reply_text(
        welcome
        + "\n".join(_USERNAME_VARIANT.format(num=num, username=username) for num, username in username_list.items())
    )

    return FriendStates.INPUT

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from app.internal.services.friend import get_friendship_username_list
from app.internal.transport.bot.modules.friends.FriendStates import FriendStates

_USERNAME_VARIANT = "{num}) {username}"


def send_username_list(
    update: Update, context: CallbackContext, list_empty_message: str, usernames_session: str, welcome: str
) -> int:
    usernames = get_friendship_username_list(update.effective_user.id)

    if not usernames:
        update.message.reply_text(list_empty_message)
        return ConversationHandler.END

    username_list = dict((num, username) for num, username in enumerate(usernames, start=1))
    context.user_data[usernames_session] = username_list

    update.message.reply_text(
        welcome + "\n".join(_USERNAME_VARIANT.format(num=num, username=username) for num, username in username_list.items())
    )

    return FriendStates.INPUT

from typing import Callable, Optional

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from app.internal.services.user import get_user

_UNDEFINED_PHONE = "Вы забыли уведомить нас о вашей мобилке. Пожалуйста, продиктуйте! (команда /set_phone)"


def if_phone_is_set(handler: Callable) -> Callable:
    def wrapper(update: Update, context: CallbackContext) -> Optional[int]:
        user = get_user(update.effective_user.id)

        if user and user.phone:
            return handler(update, context)

        update.message.reply_text(_UNDEFINED_PHONE)

        return ConversationHandler.END

    return wrapper

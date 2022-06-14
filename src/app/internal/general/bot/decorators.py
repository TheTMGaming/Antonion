from typing import Callable, Optional

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from app.internal.general.bot.handlers import COMMAND, IN_CONVERSATION
from app.internal.user.db.repositories import TelegramUserRepository

_USER_DOESNT_EXIST = "Моя вас не знать. Моя предложить знакомиться с вами! (команда /start)"
_UNDEFINED_PHONE = "Вы забыли уведомить нас о вашей мобилке. Пожалуйста, продиктуйте! (команда /phone)"
_UNDEFINED_USERNAME = "Пожалуйста, установите никнейм в телеграме, а то банк вам не доверяет"

_MUST_CONVERSATION_END = "Вы не завершили команду /{command}. Это можно сделать с помощью /cancel"


user_repo = TelegramUserRepository()


def if_update_message_exists(handler: Callable) -> Callable:
    def wrapper(update: Update, context: CallbackContext) -> Optional[int]:
        if update.message is None:
            return

        return handler(update, context)

    return wrapper


def if_user_is_created(phone=True) -> Callable:
    def handler_wrapper(handler: Callable) -> Callable:
        def wrapper(update: Update, context: CallbackContext) -> Optional[int]:
            user = user_repo.get_user(update.effective_user.id)

            if not user:
                update.message.reply_text(_USER_DOESNT_EXIST)
                return ConversationHandler.END

            if not user.username:
                update.message.reply_text(_UNDEFINED_USERNAME)
                return ConversationHandler.END

            if phone and not user.phone:
                update.message.reply_text(_UNDEFINED_PHONE)
                return ConversationHandler.END

            return handler(update, context)

        return wrapper

    return handler_wrapper


def if_user_is_not_in_conversation(handler: Callable) -> Callable:
    def wrapper(update: Update, context: CallbackContext) -> Optional[int]:
        if context.user_data.get(IN_CONVERSATION):
            command = context.user_data[COMMAND]

            update.message.reply_text(_MUST_CONVERSATION_END.format(command=command))
            return None

        return handler(update, context)

    return wrapper

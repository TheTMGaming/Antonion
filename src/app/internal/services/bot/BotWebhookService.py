from telegram import Bot, Update
from telegram.ext import CommandHandler, Dispatcher

from app.internal.transport.bot import (
    handle_getting_balance_by_account,
    handle_getting_balance_by_card,
    handle_me,
    handle_set_phone,
    handle_start,
)


class BotWebhookService:
    def __init__(self, token: str):
        self.bot = Bot(token)
        self.dispatcher = Dispatcher(self.bot, update_queue=None)

        handlers = [
            CommandHandler("start", handle_start),
            CommandHandler("set_phone", handle_set_phone),
            CommandHandler("me", handle_me),
            CommandHandler("balance", handle_getting_balance_by_account),
            CommandHandler("card_balance", handle_getting_balance_by_card),
        ]

        for handler in handlers:
            self.dispatcher.add_handler(handler)

    def handle(self, json: dict) -> None:
        update = Update.de_json(json, self.bot)
        self.dispatcher.process_update(update)

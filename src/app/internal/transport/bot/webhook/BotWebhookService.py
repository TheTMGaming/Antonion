from telegram import Bot, Update
from telegram.ext import Dispatcher

from app.internal.transport.bot.handlers import handlers


class BotWebhookService:
    def __init__(self, token: str):
        self.bot = Bot(token)
        self.dispatcher = Dispatcher(self.bot, update_queue=None)

        for handler in handlers:
            self.dispatcher.add_handler(handler)

    def handle(self, json: dict) -> None:
        update = Update.de_json(json, self.bot)
        self.dispatcher.process_update(update)

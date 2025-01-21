import logging

from aiogram import BaseMiddleware, Bot
from aiogram.client.session.middlewares.base import BaseRequestMiddleware, NextRequestMiddlewareType
from aiogram.methods import SendMessage
from aiogram.methods.base import TelegramType, Response
from aiogram.types import Message

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class LoggingMessageMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        logging.info(f"{event.from_user.first_name} {event.from_user.last_name}: {event.text}")
        return await handler(event, data)


class RequestLogging(BaseRequestMiddleware):
    async def __call__(
            self,
            make_request: NextRequestMiddlewareType[TelegramType],
            bot: Bot,
            method: SendMessage,
    ) -> Response[TelegramType]:
        if type(method) == SendMessage:
            logging.info(f"Bot: {method.text}")
        return await make_request(bot, method)

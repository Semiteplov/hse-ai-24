import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from dotenv import load_dotenv

from handlers import user_router
from middleware import RequestLogging


async def set_bot_commands(bot: Bot):
    """
    Устанавливает список доступных команд для бота.
    """
    commands = [
        BotCommand(command="/set_profile", description="Настроить профиль"),
        BotCommand(command="/log_water", description="Записать потребление воды"),
        BotCommand(command="/log_food", description="Записать потребление еды"),
        BotCommand(command="/log_workout", description="Записать тренировку"),
        BotCommand(command="/check_progress", description="Показать ваш прогресс"),
        BotCommand(command="/progress_chart", description="Показать график прогресса"),
        BotCommand(command="/recommendations", description="Рекомендации по продуктам и тренировкам"),
    ]

    await bot.set_my_commands(commands)


async def main():
    load_dotenv()
    bot = Bot(token=os.getenv('TG_BOT_TOKEN'))
    bot.session.middleware(RequestLogging())
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(user_router)

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), on_startup=set_bot_commands)
    finally:
        await bot.session.close()
        await bot.delete_webhook(drop_pending_updates=True)


if __name__ == '__main__':
    asyncio.run(main())

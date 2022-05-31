import asyncio
import logging

from aiogram import Bot, F
from aiogram.types import BotCommand

from film_bot.apps.bot.filters.base_filters import UserFilter
from film_bot.apps.bot.handlers.admin import register_admin_handlers
from film_bot.apps.bot.handlers.common import register_common
from film_bot.apps.bot.handlers.errors.errors_handlers import register_error
from film_bot.apps.bot.handlers.utils import init_chats
from film_bot.apps.bot.middleware.bot_middleware import BotMiddleware
from film_bot.config.logg_settings import init_logging
from film_bot.db import init_db
from film_bot.loader import bot, dp


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Главное меню"),
        BotCommand(command="/admin", description="Админ меню"),
    ]
    await bot.set_my_commands(commands)


async def start():
    # Настройка логирования
    init_logging(
        old_logger=True,
        level="TRACE",
        # old_level=logging.DEBUG,
        old_level=logging.INFO,
        steaming=True,
        write=True,
    )
    # Инициализация бд
    await init_db()

    # dp.startup.register(on_startup)
    # dp.shutdown.register(on_shutdown)

    # Установка команд бота
    await set_commands(bot)
    dp.message.filter(F.chat.type == "private")
    # dp.message.filter(UserFilter())
    # dp.callback_query.filter(UserFilter())
    # Регистрация хэндлеров
    # Меню админа
    register_admin_handlers(dp)
    register_common(dp)
    register_error(dp)

    # Регистрация middleware
    middleware = BotMiddleware()
    dp.message.outer_middleware(middleware)
    dp.callback_query.outer_middleware(middleware)

    # Регистрация фильтров

    await init_chats()
    await dp.start_polling(bot, skip_updates=True)


def main():
    asyncio.run(start())
    asyncio.get_event_loop()


if __name__ == "__main__":
    main()

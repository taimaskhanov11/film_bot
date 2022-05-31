from typing import Any

from aiogram import Dispatcher
from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18nMiddleware, I18n
from loguru import logger

from film_bot.config.config import I18N_DOMAIN, LOCALES_DIR
from film_bot.db.models import User


class ACLMiddleware(I18nMiddleware):

    async def get_locale(self, event: TelegramObject,data: dict[str, Any]) -> str:
        # print(f"{event=}|{data=}")
        # return users_locales.get(user.id) or user.locale
        logger.debug(f"Get locale {data['user'].user_id}")
        return data["user"].locale
        return "en"


def setup_lang_middleware(dp: Dispatcher) -> ACLMiddleware:
    # Устанавливаем миддлварь
    i18n = ACLMiddleware(I18n(path=LOCALES_DIR, domain=I18N_DOMAIN))
    dp.message.middleware(i18n)
    return i18n

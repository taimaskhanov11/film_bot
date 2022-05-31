from aiogram import types
from aiogram.dispatcher.filters import BaseFilter
from loguru import logger

from film_bot.apps.bot.handlers.utils import channel_status_check
from film_bot.db.models import User


class UserFilter(BaseFilter):
    async def __call__(self, update: types.CallbackQuery | types.Message) -> dict[str, User] | bool:
        user = update.from_user
        logger.debug(f"Filter for User {user.id}")
        user, is_new = await User.get_or_create(
            user_id=user.id,
            defaults={
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "language": user.language_code,
            },
        )
        data = {"user": user, "is_new": False}
        if is_new:
            data.update(is_new=True)
            logger.info(f"Новый пользователь {user=}")
        return data


class ChannelSubscriptionFilter(BaseFilter):
    async def __call__(self, message: types.Message | types.CallbackQuery, user:User):
        if isinstance(message, types.CallbackQuery):
            message = message.message
        if await channel_status_check(message.from_user.id):
            return {"is_sub": True}
        return {"is_sub": False}

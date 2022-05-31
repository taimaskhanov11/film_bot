from aiogram import Dispatcher, Router, F

from film_bot.config.config import config
from .admin_menu import register_admin
from .bot_settings import register_bot_settings
from .making_film import register_marking_film
from .send_mail_handers import register_send_mail
from .statistics_menu import register_statistics
from .subscriptions import register_subscriptions
from ...filters.base_filters import UserFilter

ADMIN_ROUTER = Router()


def register_admin_handlers(dp: Dispatcher):

    ADMIN_ROUTER.message.filter(F.from_user.id.in_(config.bot.admins))
    ADMIN_ROUTER.callback_query.filter(F.from_user.id.in_(config.bot.admins))

    # ADMIN_ROUTER.message.filter(UserFilter())
    # ADMIN_ROUTER.callback_query.filter(UserFilter())

    register_admin(ADMIN_ROUTER)
    register_marking_film(ADMIN_ROUTER)
    register_send_mail(ADMIN_ROUTER)
    register_bot_settings(ADMIN_ROUTER)
    register_statistics(ADMIN_ROUTER)
    register_subscriptions(ADMIN_ROUTER)

    dp.include_router(ADMIN_ROUTER)

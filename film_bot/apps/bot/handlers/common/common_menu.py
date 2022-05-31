from aiogram import Dispatcher, Router, types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from loguru import logger

from film_bot.apps.bot import temp
from film_bot.apps.bot.callback_data.base_callback import LocaleCallback, LocaleEnum
from film_bot.apps.bot.filters.base_filters import ChannelSubscriptionFilter
from film_bot.apps.bot.handlers.utils import channel_status_check
from film_bot.apps.bot.markups.common import common_markups
from film_bot.apps.bot.temp import SUBSCRIPTION_CHANNELS
from film_bot.db.models import User
from film_bot.db.models.base import Film
from film_bot.loader import _

router = Router()


class ChoiceLange(StatesGroup):
    choice = State()


class FilmStates(StatesGroup):
    choice = State()


async def check_subscribe(call: types.CallbackQuery,user:User, state: FSMContext):
    # print(user)
    await state.clear()
    if await channel_status_check(call.from_user.id):
        await call.message.answer(_("✅ Подписки найдены, введите /start чтобы продолжить"))
        return True
    # todo 5/31/2022 9:45 AM taima: почему-то не отправляет казакский язык
    # await call.answer(_("❌ Ты подписался не на все каналы", locale="kk"), show_alert=True)
    await call.answer(_("❌ Ты подписался не на все каналы"), show_alert=True)
    return False


async def start(message: types.Message | types.CallbackQuery,
                is_sub: bool,
                is_new: bool,
                state: FSMContext):
    await state.clear()
    if isinstance(message, types.CallbackQuery):
        message = message.message
    if is_new:
        await message.answer("🇷🇺 На каком языке продолжить?\n"
                             "🇰🇿 Қай тілде жалғастыру керек?", reply_markup=common_markups.start_for_new_user())
        return
    if not is_sub:
        await message.answer(_(f"📍 Для того, чтобы пользоваться ботом, нужно подписаться на каналы:"),
                             reply_markup=common_markups.channel_status_check(SUBSCRIPTION_CHANNELS))
        return

    await message.answer(_("🎥 Введите номер фильма, который вы хотите посмотреть:"),
                         reply_markup=common_markups.start_menu())
    await state.set_state(FilmStates.choice)


async def get_file(message: types.Message, is_sub: bool, state: FSMContext):
    if not is_sub:
        await message.answer(_(f"📍 Для того, чтобы пользоваться ботом, нужно подписаться на каналы:"),
                             reply_markup=common_markups.channel_status_check(SUBSCRIPTION_CHANNELS))
        return
    try:
        if message.text.isdigit():
            film = await Film.get(custom_id=message.text)
            await film.send(message)
            temp.TODAY_DOWNLOADS += 1
            await state.clear()
            return
    except Exception as e:
        logger.warning(e)
    await message.answer(_("❌ Введён неправильный номер фильма, повторите попытку"))


async def start_for_new_user(message: types.Message, state: FSMContext):
    await message.answer("🇷🇺 На каком языке продолжить?\n"
                         "🇰🇿 Қай тілде жалғастыру керек?", reply_markup=common_markups.start_for_new_user())
    await state.set_state(ChoiceLange.choice)


async def language_choice(call: types.CallbackQuery):
    await call.message.answer("🇷🇺 На каком языке продолжить?\n"
                              "🇰🇿 Қай тілде жалғастыру керек?", reply_markup=common_markups.start_for_new_user())


async def locale_choice(call: types.CallbackQuery, user: User, callback_data: LocaleCallback, state: FSMContext):
    if callback_data.locale is LocaleEnum.ru:
        user.locale = LocaleEnum.ru.value
    else:
        user.locale = LocaleEnum.kk.value
    await user.save(update_fields=["locale"])
    await call.message.answer(_("✅ Язык успешно выбран, введите /start чтобы продолжить", locale=user.locale))
    # await call.message.answer(_("🎥 Введите номер фильма, который вы хотите посмотреть:", locale=user.locale),
    #                           reply_markup=common_markups.menu()
    # )
    await state.clear()


def register_common(dp: Dispatcher):
    dp.include_router(router)

    callback = router.callback_query.register
    message = router.message.register

    # router.message.filter(UserFilter())
    # router.callback_query.filter(UserFilter())

    message(start, ChannelSubscriptionFilter(), commands="start", state="*")
    callback(start, ChannelSubscriptionFilter(), text="start", state="*")

    callback(check_subscribe, text="check_subscribe", state="*")

    callback(language_choice, text="language_choice", state="*")
    callback(locale_choice, LocaleCallback.filter(), state="*")
    message(get_file, ChannelSubscriptionFilter(), state=FilmStates.choice)
    message(get_file, ChannelSubscriptionFilter())

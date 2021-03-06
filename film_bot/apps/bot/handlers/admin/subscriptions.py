from aiogram import F, Router, types
from aiogram.dispatcher.fsm.context import FSMContext
# from aiogram.dispatcher.filters
from aiogram.dispatcher.fsm.state import StatesGroup, State
from loguru import logger

from film_bot.apps.bot.callback_data.base_callback import ChatCallback
from film_bot.apps.bot.handlers.utils import parse_channel_link
from film_bot.apps.bot.markups.admin import subscriptions_markups, admin_markups
from film_bot.db.models.base import Chat

router = Router()


class NewChat(StatesGroup):
    done = State()


class NewSponsorChat(StatesGroup):
    done = State()


async def view_chats(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    chats = await Chat.all()
    await call.message.answer(f"Все чаты для обязательной подписки:",
                              reply_markup=subscriptions_markups.view_chats(chats))


async def new_chat(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer(f"Добавьте бота в чат и сделайте администратором, чтобы проверять подписки.\n"
                              f"Введите ссылку на канал. "
                              f"Введите ссылку по которому должны будут пройти пользователи и через пробел фактическую ссылку на канал для проверки ботом\n"
                              f"Например:\n"
                              f"https://t.me/+bIBc0e-525k2MThi https://t.me/mychannel",
                              reply_markup=admin_markups.back())
    await state.set_state(NewChat.done)


async def new_chat_done(message: types.Message, state: FSMContext):
    try:
        await state.clear()
        skin, link = parse_channel_link(message.text)
        chat = await Chat.create(skin=skin, link=link)
        await message.answer(f"Чат для подписки: {chat}\n успешно добавлен", reply_markup=admin_markups.back())
    except Exception as e:
        logger.warning(e)
        await message.answer("Неправильный ввод", reply_markup=admin_markups.back())


async def touch_chat(call: types.CallbackQuery, callback_data: ChatCallback, state: FSMContext):
    await state.clear()
    chat = await Chat.get(pk=callback_data.pk)
    await call.message.answer(f"{chat}",
                              reply_markup=subscriptions_markups.touch_chat(chat))


async def delete_chat(call: types.CallbackQuery, callback_data: ChatCallback, state: FSMContext):
    await state.clear()
    await state.update_data(delete_chat=callback_data.pk)
    chat = await Chat.get(pk=callback_data.pk)
    await chat.delete()
    await call.message.answer(f"Канал для подписки: {chat} успешно удален")


def register_subscriptions(dp: Router):
    dp.include_router(router)

    callback = router.callback_query.register
    message = router.message.register

    callback(view_chats, ChatCallback.filter(F.action == "view"), state="*")
    callback(new_chat, ChatCallback.filter(F.action == "new"), state="*")
    message(new_chat_done, state=NewChat.done)
    callback(touch_chat, ChatCallback.filter(F.action == "touch"), state="*")
    callback(delete_chat, ChatCallback.filter(F.action == "delete"), state="*")

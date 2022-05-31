from aiogram import Router, types, F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from loguru import logger

from film_bot.apps.bot.callback_data.base_callback import FilmCallback
from film_bot.apps.bot.markups.admin import making_film_markups, admin_markups
from film_bot.db.models.base import Film

router = Router()


class CreateFilm(StatesGroup):
    number = State()
    file = State()


async def view_all_films(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    films = await Film.all()
    await call.message.answer("Текущие фильмы:\n", reply_markup=making_film_markups.view_all_films(films))


async def view_film(call: types.CallbackQuery, callback_data: FilmCallback, state: FSMContext):
    await state.clear()
    film = await Film.get(pk=callback_data.pk)
    await call.message.answer_photo(film.file_id, caption=film.caption,
                                    reply_markup=making_film_markups.view_film(film))


async def delete_film(call: types.CallbackQuery, callback_data: FilmCallback, state: FSMContext):
    await state.clear()
    chat = await Film.get(pk=callback_data.pk)
    await chat.delete()
    await call.message.answer(f"Фильм: {chat} успешно удален")


async def create_film(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("Отправьте цифры для фильма", reply_markup=admin_markups.back())
    await state.set_state(CreateFilm.number)


async def create_film_number(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(custom_id=message.text)
        if await Film.get_or_none(custom_id=message.text):
            await message.answer(f"Фильм под таким номером уже существует")
            return
        await message.answer("Отправьте фото с прикрепленным текстом", reply_markup=admin_markups.back())
        await state.set_state(CreateFilm.file)
    else:
        await message.answer("неправильный ввод")


async def create_film_file(message: types.Message, state: FSMContext):
    logger.debug(message)
    if message.photo:
        data = await state.get_data()
        photo = message.photo[-1]
        await Film.create(
            # text=message.caption,
            custom_id=data["custom_id"],
            file_id=photo.file_id,
            file_type="photo",
            caption=message.caption
        )
        await message.answer(f"Фильм успешно создан",reply_markup= admin_markups.back())

    else:
        await message.answer("Неправильный ввод, отправьте фото")


def register_marking_film(dp: Router):
    dp.include_router(router)

    callback = router.callback_query.register
    message = router.message.register

    callback(view_all_films, FilmCallback.filter(F.action == "view_all"))
    callback(view_film, FilmCallback.filter(F.action == "view"))
    callback(delete_film, FilmCallback.filter(F.action == "delete"))

    callback(create_film, FilmCallback.filter(F.action == "create"))
    message(create_film_number, state=CreateFilm.number)
    message(create_film_file, state=CreateFilm.file)

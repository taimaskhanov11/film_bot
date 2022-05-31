from film_bot.apps.bot.callback_data.base_callback import FilmCallback
from film_bot.apps.bot.markups.admin.admin_markups import admin_back_buttons
from film_bot.apps.bot.markups.utils import get_inline_keyboard, get_as_column
from film_bot.db.models.base import Film


def view_all_films(films: list[Film]):
    keyboard = [
        [f"{c}", FilmCallback(pk=c.pk, action="view").pack()] for c in films
    ]
    # print(keyboard)
    keyboard.append(admin_back_buttons)
    return get_inline_keyboard(get_as_column(keyboard, 1))


def view_film(film):
    keyboard = [
        [(f"✍ Удалить [{film.custom_id}].", FilmCallback(pk=film.pk, action="delete").pack())]
    ]
    keyboard.append([admin_back_buttons])
    return get_inline_keyboard(keyboard)

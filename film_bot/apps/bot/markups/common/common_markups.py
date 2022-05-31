from film_bot.apps.bot.callback_data.base_callback import LocaleCallback, LocaleEnum
from film_bot.apps.bot.markups.utils import get_inline_keyboard, get_as_column, get_inline_url_keyboard, \
    get_inline_button
from film_bot.loader import _


def start_menu():
    keyboard = [
        ((_("🇷🇺🇰🇿 Сменить язык"), "language_choice"),),
    ]
    return get_inline_keyboard(keyboard)


def channel_status_check(channels: list[tuple[str, str]]):
    keyboard = []
    for num, skin in enumerate(channels, 1):
        keyboard.append(
            (f"Канал #{num}", f"https://t.me/{skin[1][1:]}"),
        )
    column_keyboard = get_as_column(keyboard)
    ikeyboard = get_inline_url_keyboard(column_keyboard)
    inline_button = get_inline_button((_("✅ Я подписался"), "check_subscribe"))
    ikeyboard.inline_keyboard.append([inline_button])
    return ikeyboard


def start_for_new_user():
    keyboard = [
        (("Қазақ тілі", LocaleCallback(locale=LocaleEnum.kk).pack()),
         ("Русский язык", LocaleCallback(locale=LocaleEnum.ru).pack())),
    ]
    return get_inline_keyboard(keyboard)




def menu():
    keyboard = [
        ((_("Меню"), "start"),),
    ]
    return get_inline_keyboard(keyboard)

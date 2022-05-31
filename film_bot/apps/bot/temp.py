import typing

if typing.TYPE_CHECKING:
    from film_bot.apps.bot.handlers.utils import MailSender

SUBSCRIPTION_CHANNELS: list[tuple[str, str]] = []
MAIL_SENDER: typing.Optional["MailSender"] = None
BOT_RUNNING: bool = True
ONLINE_USERS: dict[int, bool] = {}
TODAY_DOWNLOADS: int = 0

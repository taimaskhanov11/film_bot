import datetime
import typing
from functools import partial

from aiogram import types
from aiogram.types import BufferedInputFile, FSInputFile
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_queryset_creator, PydanticListModel

from film_bot.apps.bot import temp

__all__ = (
    "User",
    "Chat",
    "Film"
)

from film_bot.config.config import MEDIA_DIR


class Film(models.Model):
    text = fields.TextField(null=True)
    custom_id = fields.IntField(index=True, unique=True)
    file_id = fields.CharField(100, null=True, index=True)
    file_type = fields.CharField(10, null=True, description="")
    caption = fields.TextField(null=True)
    path = fields.CharField(255, unique=True, null=True)

    def __str__(self):
        return str(self.custom_id)

    async def send(self, message: types.Message):
        # method = getattr(message, f"answer_{self.file_type}")
        _method = getattr(message, f"answer_{self.file_type}")
        method = partial(_method, caption=self.caption)
        # method = partial(_method, caption=self.caption)
        if self.file_id:
            await method(self.file_id)
        else:
            if "https" in self.path or "http" in self.path:
                message = await method(self.path)
            else:
                message = await method(FSInputFile(MEDIA_DIR / self.path))
            file = getattr(message, self.file_type)
            if self.file_type == "photo":
                self.file_id = file[0].file_id
            else:
                self.file_id = file.file_id
            await self.save(update_fields=["file_id"])


class User(models.Model):
    user_id = fields.BigIntField(index=True, unique=True)
    username = fields.CharField(32, unique=True, index=True, null=True)
    first_name = fields.CharField(255, null=True)
    last_name = fields.CharField(255, null=True)
    locale = fields.CharField(32, default="ru")
    registered_at = fields.DatetimeField(auto_now_add=True)

    @classmethod
    async def export_users(cls,
                           _fields: tuple[str],
                           _to: typing.Literal["text", "txt", "json"]) -> BufferedInputFile | str:
        UserPydanticList = pydantic_queryset_creator(User, include=_fields)
        users: PydanticListModel = await UserPydanticList.from_queryset(User.all())
        if _to == "text":
            users_list = list(users.dict()["__root__"])
            user_value_list = list(map(lambda x: str(list(x.values())), users_list))
            result = "\n".join(user_value_list)
        elif _to == "txt":
            users_list = list(users.dict()["__root__"])
            user_value_list = list(map(lambda x: str(list(x.values())), users_list))
            user_txt = "\n".join(user_value_list)
            result = BufferedInputFile(bytes(user_txt, "utf-8"), filename="users.txt")
        else:
            # json.dumps(ensure_ascii=False, default=str)
            result = BufferedInputFile(bytes(users.json(ensure_ascii=False), "utf-8"),
                                       filename="users.json")
        return result

    @classmethod
    async def count_all(cls):
        return await cls.all().count()

    @classmethod
    async def count_new_today(cls) -> int:
        return await cls.filter(registered_at=datetime.date.today()).count()

    async def set_language(self, language: typing.Literal["ru", "kk"]):
        self.locale = language
        await self.save(update_fields=["language"])


class Chat(models.Model):
    skin = fields.CharField(100, index=True)
    link = fields.CharField(100, index=True)
    views = fields.IntField(default=0)

    def __str__(self):
        return f"{self.skin} [{self.link}]."

    @classmethod
    async def create(cls, **kwargs):
        print(temp.SUBSCRIPTION_CHANNELS)
        temp.SUBSCRIPTION_CHANNELS.append((kwargs.get("skin"), kwargs.get("link")))
        return await super().create(**kwargs)

    async def delete(self, using_db=None) -> None:
        print(temp.SUBSCRIPTION_CHANNELS)
        temp.SUBSCRIPTION_CHANNELS.remove(self.tuple)
        await super().delete(using_db)

    @property
    def tuple(self) -> tuple[str, str]:
        return self.skin, self.link

    def add_to_temp(self):
        temp.SUBSCRIPTION_CHANNELS.append(self.tuple)

    def remove_from_temp(self):
        temp.SUBSCRIPTION_CHANNELS.remove(self.tuple)

import asyncpg
import tortoise
from loguru import logger
from tortoise import Tortoise

__all__ = (
    "MODELS_DIR",
    "init_db",
    "models",
    "utils"
)

from film_bot.config.config import Database, config

MODELS_DIR = "film_bot.db.models"


async def init_db(db: Database = config.db):
    logger.debug(f"Initializing Database {db.db_name}[{db.host}]...")
    data = {
        "db_url": db.postgres_url,
        "modules": {"models": [MODELS_DIR]},
    }
    try:
        await Tortoise.init(**data)
        await Tortoise.generate_schemas()
    except (asyncpg.exceptions.ConnectionDoesNotExistError,
            tortoise.exceptions.DBConnectionError) as e:
        logger.warning(e)
        logger.info("Creating a new database ...")
        await Tortoise.init(**data, _create_db=True)
        await Tortoise.generate_schemas()
        logger.success(f"New database {db.db_name} created")

    logger.debug(f"Database {db.db_name}[{db.host}] initialized")

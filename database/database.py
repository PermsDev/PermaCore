import os

from dotenv import load_dotenv
from asyncmy import create_pool


load_dotenv()


core_pool = None
main_pool = None
guild_pool = None


async def init_database():
    global core_pool, main_pool, guild_pool

    # ======================
    # CORE DATABASE
    # ======================

    if core_pool is None:
        core_pool = await create_pool(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            db=os.getenv("DB_NAME"),

            minsize=5,
            maxsize=10,

            autocommit=True,
            pool_recycle=300
        )

    # ======================
    # MAIN DATABASE
    # ======================

    if main_pool is None:
        main_pool = await create_pool(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            db=os.getenv("MAIN_DB_NAME"),

            minsize=5,
            maxsize=10,

            autocommit=True,
            pool_recycle=300
        )

    # ======================
    # GUILD DATABASE
    # ======================

    if guild_pool is None:
        guild_pool = await create_pool(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            db=os.getenv("GUILD_DB_NAME"),

            minsize=5,
            maxsize=10,

            autocommit=True,
            pool_recycle=300
        )


def get_core_pool():
    return core_pool


def get_main_pool():
    return main_pool


def get_guild_pool():
    return guild_pool


async def close_database():
    global core_pool, main_pool, guild_pool

    # ======================
    # CORE
    # ======================

    if core_pool is not None:
        core_pool.close()
        await core_pool.wait_closed()
        core_pool = None

    # ======================
    # MAIN
    # ======================

    if main_pool is not None:
        main_pool.close()
        await main_pool.wait_closed()
        main_pool = None

    # ======================
    # GUILD
    # ======================

    if guild_pool is not None:
        guild_pool.close()
        await guild_pool.wait_closed()
        guild_pool = None
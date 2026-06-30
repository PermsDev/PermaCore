import os

from dotenv import load_dotenv
from asyncmy import create_pool

load_dotenv()

pool = None


async def init_database():
    global pool

    if pool is None:
        pool = await create_pool(
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


def get_pool():
    return pool
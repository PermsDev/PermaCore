# database/intro_manager.py

from database.database import get_pool


# ======================
# USER PROFILE
# ======================

async def get_user_profile(
    guild_id: int,
    user_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    user_id,
                    guild_id,
                    nickname,
                    joined_at
                FROM user_db
                WHERE guild_id = %s
                  AND user_id = %s
            """, (
                guild_id,
                user_id
            ))

            row = await cursor.fetchone()

            if row is None:
                return {}

            profile = {
                "user_id": row[0],
                "guild_id": row[1],
                "nickname": row[2],
                "joined_at": row[3],
                "games": {}
            }

            await cursor.execute("""
                SELECT
                    game_key,
                    value,
                    message_id,
                    channel_id
                FROM intro_db
                WHERE guild_id = %s
                  AND user_id = %s
            """, (
                guild_id,
                user_id
            ))

            rows = await cursor.fetchall()

            for intro in rows:
                profile["games"][intro[0]] = {
                    "value": intro[1],
                    "message_id": intro[2],
                    "channel_id": intro[3]
                }

            return profile


async def save_user_profile(
    guild_id: int,
    user_id: int,
    nickname: str,
    joined_at
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                INSERT INTO user_db (
                    user_id,
                    guild_id,
                    nickname,
                    joined_at
                )
                VALUES (%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    nickname=VALUES(nickname),
                    joined_at=VALUES(joined_at)
            """, (
                user_id,
                guild_id,
                nickname,
                joined_at
            ))

            await conn.commit()


# ======================
# INTRO DATA
# ======================

async def get_user_intro(
    guild_id: int,
    user_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    user_id,
                    guild_id,
                    game_key,
                    value,
                    message_id,
                    channel_id
                FROM intro_db
                WHERE guild_id=%s
                  AND user_id=%s
            """, (
                guild_id,
                user_id
            ))

            rows = await cursor.fetchall()

            return [
                {
                    "user_id": r[0],
                    "guild_id": r[1],
                    "game_key": r[2],
                    "value": r[3],
                    "message_id": r[4],
                    "channel_id": r[5]
                }
                for r in rows
            ]


async def get_game_intro(
    guild_id: int,
    user_id: int,
    game_key: str
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    user_id,
                    guild_id,
                    game_key,
                    value,
                    message_id,
                    channel_id
                FROM intro_db
                WHERE guild_id=%s
                  AND user_id=%s
                  AND game_key=%s
            """, (
                guild_id,
                user_id,
                game_key
            ))

            row = await cursor.fetchone()

            if row is None:
                return None

            return {
                "user_id": row[0],
                "guild_id": row[1],
                "game_key": row[2],
                "value": row[3],
                "message_id": row[4],
                "channel_id": row[5]
            }


async def save_intro(
    guild_id: int,
    user_id: int,
    game_key: str,
    value: str,
    message_id: int,
    channel_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                INSERT INTO intro_db(
                    user_id,
                    guild_id,
                    game_key,
                    value,
                    message_id,
                    channel_id
                )
                VALUES(%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    value=VALUES(value),
                    message_id=VALUES(message_id),
                    channel_id=VALUES(channel_id)
            """, (
                user_id,
                guild_id,
                game_key,
                value,
                message_id,
                channel_id
            ))

            await conn.commit()


async def delete_intro(
    guild_id: int,
    user_id: int,
    game_key: str
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                DELETE FROM intro_db
                WHERE guild_id=%s
                  AND user_id=%s
                  AND game_key=%s
            """, (
                guild_id,
                user_id,
                game_key
            ))

            await conn.commit()


async def delete_all_user_intro(
    guild_id: int,
    user_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                DELETE FROM intro_db
                WHERE guild_id=%s
                  AND user_id=%s
            """, (
                guild_id,
                user_id
            ))

            await conn.commit()


async def delete_user_profile(
    guild_id: int,
    user_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                DELETE FROM user_db
                WHERE guild_id=%s
                  AND user_id=%s
            """, (
                guild_id,
                user_id
            ))

            await conn.commit()


# ======================
# BULK LOAD
# ======================

async def get_all_intro():
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    user_id,
                    guild_id,
                    game_key,
                    value,
                    message_id,
                    channel_id
                FROM intro_db
            """)

            rows = await cursor.fetchall()

            return [
                {
                    "user_id": r[0],
                    "guild_id": r[1],
                    "game_key": r[2],
                    "value": r[3],
                    "message_id": r[4],
                    "channel_id": r[5]
                }
                for r in rows
            ]


async def get_copyview_intros():
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    user_id,
                    game_key,
                    message_id
                FROM intro_db
                WHERE game_key IN (
                    'mlbb',
                    'roblox'
                )
            """)

            rows = await cursor.fetchall()

            return [
                {
                    "user_id": r[0],
                    "game_key": r[1],
                    "message_id": r[2]
                }
                for r in rows
            ]
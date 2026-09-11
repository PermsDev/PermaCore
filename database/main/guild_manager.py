from database.database import get_main_pool as get_pool
from asyncmy.cursors import DictCursor


# ==================================================
# GET ALL GUILD IDS
# ==================================================
async def get_all_guild_ids() -> list[int]:
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT guild_id
                FROM guild_db
                ORDER BY guild_name
            """)

            rows = await cursor.fetchall()

    return [row[0] for row in rows]


# ==================================================
# GET ALL GUILDS
# ==================================================
async def get_all_guilds() -> list[dict]:
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:
            await cursor.execute("""
                SELECT
                    guild_id,
                    guild_name,
                    created_at,
                    updated_at
                FROM guild_db
                ORDER BY guild_name
            """)

            return await cursor.fetchall()


# ==================================================
# GET GUILD
# ==================================================
async def get_guild(guild_id: int):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:
            await cursor.execute("""
                SELECT
                    guild_id,
                    guild_name,
                    created_at,
                    updated_at
                FROM guild_db
                WHERE guild_id = %s
            """, (
                guild_id,
            ))

            return await cursor.fetchone()


# ==================================================
# CHECK GUILD EXISTS
# ==================================================
async def guild_exists(guild_id: int) -> bool:
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT 1
                FROM guild_db
                WHERE guild_id = %s
                LIMIT 1
            """, (
                guild_id,
            ))

            return await cursor.fetchone() is not None


# ==================================================
# ADD / UPDATE GUILD
# ==================================================
async def add_guild(
    guild_id: int,
    guild_name: str
):
    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO guild_db (
                        guild_id,
                        guild_name
                    )
                    VALUES (%s, %s) 

                    ON DUPLICATE KEY UPDATE
                        guild_name = VALUES(guild_name)
                """, (
                    guild_id,
                    guild_name
                ))

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise


# ==================================================
# UPDATE GUILD NAME
# ==================================================
async def update_guild_name(
    guild_id: int,
    guild_name: str
):
    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    UPDATE guild_db
                    SET guild_name = %s
                    WHERE guild_id = %s
                """, (
                    guild_name,
                    guild_id
                ))

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise


# ==================================================
# REMOVE GUILD
# ==================================================
async def remove_guild(
    guild_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    DELETE FROM guild_db
                    WHERE guild_id = %s
                """, (
                    guild_id,
                ))

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise
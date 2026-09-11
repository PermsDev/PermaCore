from database.database import get_main_pool as get_pool
from asyncmy.cursors import DictCursor


# ==================================================
# GET ALL GUILDS OF A BOT
# ==================================================
async def get_guilds_by_bot(
    bot_id: int
) -> list[dict]:

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute("""
                SELECT
                    bg.guild_id,
                    g.guild_name,
                    bg.joined_at
                FROM bot_guild_db bg

                INNER JOIN guild_db g
                    ON g.guild_id = bg.guild_id

                WHERE bg.bot_id = %s

                ORDER BY g.guild_name
            """, (
                bot_id,
            ))

            return await cursor.fetchall()


# ==================================================
# GET ALL BOTS OF A GUILD
# ==================================================
async def get_bots_by_guild(
    guild_id: int
) -> list[dict]:

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute("""
                SELECT
                    bg.bot_id,
                    b.bot_name,
                    bg.joined_at
                FROM bot_guild_db bg

                INNER JOIN bot_db b
                    ON b.bot_id = bg.bot_id

                WHERE bg.guild_id = %s

                ORDER BY b.bot_name
            """, (
                guild_id,
            ))

            return await cursor.fetchall()


# ==================================================
# CHECK BOT IN GUILD
# ==================================================
async def is_bot_in_guild(
    bot_id: int,
    guild_id: int
) -> bool:

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT 1
                FROM bot_guild_db
                WHERE bot_id = %s
                  AND guild_id = %s
                LIMIT 1
            """, (
                bot_id,
                guild_id
            ))

            return await cursor.fetchone() is not None


# ==================================================
# ADD BOT TO GUILD
# ==================================================
async def add_bot_to_guild(
    bot_id: int,
    guild_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:

                await cursor.execute("""
                    INSERT IGNORE INTO bot_guild_db (
                        bot_id,
                        guild_id
                    )
                    VALUES (%s, %s)
                """, (
                    bot_id,
                    guild_id
                ))

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise


# ==================================================
# REMOVE BOT FROM GUILD
# ==================================================
async def remove_bot_from_guild(
    bot_id: int,
    guild_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:

                await cursor.execute("""
                    DELETE FROM bot_guild_db
                    WHERE bot_id = %s
                      AND guild_id = %s
                """, (
                    bot_id,
                    guild_id
                ))

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise
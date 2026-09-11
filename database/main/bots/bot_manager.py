from database.database import get_main_pool as get_pool
from asyncmy.cursors import DictCursor


# ==================================================
# GET ALL BOTS
# ==================================================
async def get_all_bots() -> list[dict]:
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute("""
                SELECT
                    bot_id,
                    bot_name,
                    created_at
                FROM bot_db
                ORDER BY bot_name
            """)

            return await cursor.fetchall()


# ==================================================
# GET BOT
# ==================================================
async def get_bot(
    bot_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute("""
                SELECT
                    bot_id,
                    bot_name,
                    created_at
                FROM bot_db
                WHERE bot_id = %s
            """, (
                bot_id,
            ))

            return await cursor.fetchone()


# ==================================================
# CHECK BOT EXISTS
# ==================================================
async def bot_exists(
    bot_id: int
) -> bool:

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT 1
                FROM bot_db
                WHERE bot_id = %s
                LIMIT 1
            """, (
                bot_id,
            ))

            return await cursor.fetchone() is not None


# ==================================================
# ADD / UPDATE BOT
# ==================================================
async def add_bot(
    bot_id: int,
    bot_name: str
):
    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:

                await cursor.execute("""
                    INSERT INTO bot_db (
                        bot_id,
                        bot_name
                    )
                    VALUES (%s, %s) AS new

                    ON DUPLICATE KEY UPDATE
                        bot_name = new.bot_name
                """, (
                    bot_id,
                    bot_name
                ))

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise


# ==================================================
# UPDATE BOT NAME
# ==================================================
async def update_bot_name(
    bot_id: int,
    bot_name: str
):
    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:

                await cursor.execute("""
                    UPDATE bot_db
                    SET bot_name = %s
                    WHERE bot_id = %s
                """, (
                    bot_name,
                    bot_id
                ))

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise


# ==================================================
# REMOVE BOT
# ==================================================
async def remove_bot(
    bot_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:

                await cursor.execute("""
                    DELETE FROM bot_db
                    WHERE bot_id = %s
                """, (
                    bot_id,
                ))

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise
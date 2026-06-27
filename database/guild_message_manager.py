# database/guild_message_manager.py

from database.database import get_pool


# =========================
# GET MESSAGE
# =========================
async def get_guild_message(
    guild_id: int,
    user_id: int,
    message_type: str
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    message_id,
                    channel_id
                FROM guild_message_db
                WHERE guild_id = %s
                  AND user_id = %s
                  AND message_type = %s
                LIMIT 1
            """, (
                guild_id,
                user_id,
                message_type
            ))

            row = await cursor.fetchone()

            if row is None:
                return None

            return {
                "message_id": row[0],
                "channel_id": row[1]
            }


# =========================
# UPSERT MESSAGE
# =========================
async def upsert_guild_message(
    guild_id: int,
    user_id: int,
    message_type: str,
    channel_id: int,
    message_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                INSERT INTO guild_message_db (
                    guild_id,
                    user_id,
                    message_type,
                    channel_id,
                    message_id
                )
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    channel_id = VALUES(channel_id),
                    message_id = VALUES(message_id)
            """, (
                guild_id,
                user_id,
                message_type,
                channel_id,
                message_id
            ))

            await conn.commit()


# =========================
# DELETE MESSAGE TYPE
# =========================
async def delete_guild_message(
    guild_id: int,
    user_id: int,
    message_type: str
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                DELETE FROM guild_message_db
                WHERE guild_id = %s
                  AND user_id = %s
                  AND message_type = %s
            """, (
                guild_id,
                user_id,
                message_type
            ))

            await conn.commit()


# =========================
# GET ALL MESSAGES FOR GUILD
# =========================
async def get_all_guild_messages(
    guild_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    message_id,
                    channel_id,
                    user_id,
                    message_type
                FROM guild_message_db
                WHERE guild_id = %s
            """, (
                guild_id,
            ))

            rows = await cursor.fetchall()

            return [
                {
                    "message_id": row[0],
                    "channel_id": row[1],
                    "user_id": row[2],
                    "message_type": row[3]
                }
                for row in rows
            ]
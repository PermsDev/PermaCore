from database.database import get_pool
from asyncmy.cursors import DictCursor

# ==================================================
# membaca semua channel untuk guild tertentu
# ==================================================
async def get_channels(guild_id: int):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute("""
                SELECT channel_key, channel_id, panel_message
                FROM channel_db
                WHERE guild_id = %s
            """, (guild_id,))

            rows = await cursor.fetchall()

    return {
        row["channel_key"]: {
            "channel_id": row["channel_id"],
            "panel_message": row["panel_message"]
        }
        for row in rows
    }


# ==================================================
# membaca channel tertentu
# ==================================================
async def get_channel(guild_id: int, channel_key: str):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute("""
                SELECT channel_id, panel_message
                FROM channel_db
                WHERE guild_id = %s
                AND channel_key = %s
            """, (guild_id, channel_key))

            row = await cursor.fetchone()

    if row is None:
        return None

    return {
        "channel_id": row["channel_id"],
        "panel_message": row["panel_message"]
    }


# ==================================================
# insert / update channel
# ==================================================
async def set_channel(
    guild_id: int,
    channel_key: str,
    channel_id: int,
    panel_message: int = None
):
    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO channel_db (
                        guild_id,
                        channel_key,
                        channel_id,
                        panel_message
                    )
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        channel_id = VALUES(channel_id),
                        panel_message = VALUES(panel_message)
                """, (
                    guild_id,
                    channel_key,
                    channel_id,
                    panel_message
                ))

            await conn.commit()
            
        except Exception:
            await conn.rollback()
            raise

# ==================================================
# delete channel
# ==================================================
async def delete_channel(
    guild_id: int,
    channel_key: str
):
    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    DELETE FROM channel_db
                    WHERE guild_id = %s
                    AND channel_key = %s
                """, (
                    guild_id,
                    channel_key
                ))

            await conn.commit()
            
        except Exception:
            await conn.rollback()
            raise

# ==================================================
# game channels
# ==================================================
async def get_game_channels(guild_id: int):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute("""
                SELECT channel_key, channel_id
                FROM channel_db
                WHERE guild_id = %s
                AND channel_key IN (
                    'growtopia',
                    'pw',
                    'mlbb',
                    'roblox'
                )
            """, (guild_id,))

            rows = await cursor.fetchall()

    return {
        row["channel_key"]: row["channel_id"]
        for row in rows
    }
from database.database import get_core_pool

# ==================================================
# GET USER INTRO MESSAGES
# ==================================================

async def get_user_intro_messages(
    guild_id: int,
    user_id: int
):
    """
    Mengambil seluruh record intro_message_db
    milik user pada guild tertentu.
    """

    core_pool = get_core_pool()

    async with core_pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    game_key,
                    message_id,
                    channel_id
                FROM intro_message_db
                WHERE guild_id = %s
                AND user_id = %s
            """, (
                guild_id,
                user_id
            ))

            rows = await cursor.fetchall()

            return [
                {
                    "game_key": row[0],
                    "message_id": row[1],
                    "channel_id": row[2]
                }
                for row in rows
            ]

# =================================================
# SAVE INTRO MESSAGE ONLY
# =================================================
async def save_intro_message(
    guild_id: int,
    user_id: int,
    game_key: str,
    message_id: int,
    channel_id: int
):
    core_pool = get_core_pool()

    async with core_pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO intro_message_db (
                        guild_id,
                        user_id,
                        game_key,
                        message_id,
                        channel_id
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        message_id = VALUES(message_id),
                        channel_id = VALUES(channel_id)
                """, (
                    guild_id,
                    user_id,
                    game_key,
                    message_id,
                    channel_id
                ))

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise

# ==================================================
# DELETE USER INTRO MESSAGES
# ==================================================

async def delete_user_intro_messages(
    guild_id: int,
    user_id: int
):
    """
    Menghapus seluruh record intro_message_db
    milik user pada guild tertentu.

    Tidak menghapus data game_db.
    """

    core_pool = get_core_pool()

    async with core_pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:

                await cursor.execute("""
                    DELETE FROM intro_message_db
                    WHERE guild_id = %s
                    AND user_id = %s
                """, (
                    guild_id,
                    user_id
                ))

                deleted = cursor.rowcount

            await conn.commit()

            return deleted

        except Exception:
            await conn.rollback()
            raise
        
# ==================================================
# COPYVIEW INTROS (MLBB & ROBLOX)
# ==================================================

async def get_copyview_intros(
    guild_id: int
):
    """
    Mengambil message intro MLBB dan Roblox
    dari guild tertentu.

    DATABASE:
        permacore.intro_message_db
    """

    core_pool = get_core_pool()

    async with core_pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    m.user_id,
                    m.game_key,
                    m.message_id
                FROM intro_message_db AS m
                WHERE m.guild_id = %s
                AND m.game_key IN (
                    'mlbb',
                    'roblox'
                )
            """, (
                guild_id
            ))

            rows = await cursor.fetchall()

            return [
                {
                    "user_id": row[0],
                    "game_key": row[1],
                    "message_id": row[2]
                }
                for row in rows
            ]

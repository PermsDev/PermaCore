from database.database import get_pool
from asyncmy.cursors import DictCursor

# ==================================================
# GET USER PROTECTED DM
# ==================================================
async def get_user_dm_messages(
    user_id: int
) -> set[int]:

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute("""
                SELECT message_id
                FROM dm_message_db
                WHERE user_id = %s
            """, (
                user_id,
            ))

            rows = await cursor.fetchall()

    return {
        row["message_id"]
        for row in rows
    }

# ==================================================
# GET DM MESSAGE
# ==================================================
async def get_dm_message(
    guild_id: int,
    user_id: int,
    dm_type: str
) -> int | None:

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute("""
                SELECT message_id
                FROM dm_message_db
                WHERE guild_id = %s
                    AND user_id = %s
                    AND dm_type = %s
                LIMIT 1
            """, (
                guild_id,
                user_id,
                dm_type
            ))

            row = await cursor.fetchone()

    return row["message_id"] if row else None


# ==================================================
# UPSERT DM MESSAGE
# ==================================================
async def upsert_dm_message(
    guild_id: int,
    user_id: int,
    dm_type: str,
    message_id: int
):

    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO dm_message_db (
                        guild_id,
                        user_id,
                        dm_type,
                        message_id
                    )
                    VALUES (%s, %s, %s, %s)

                    ON DUPLICATE KEY UPDATE
                        message_id = VALUES(message_id)
                """, (
                    guild_id,
                    user_id,
                    dm_type,
                    message_id
                ))

            await conn.commit()
            
        except Exception:
            await conn.rollback()
            raise

# ==================================================
# DELETE DM MESSAGE
# ==================================================
async def delete_dm_message(
    guild_id: int,
    user_id: int,
    dm_type: str
):

    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    DELETE FROM dm_message_db
                    WHERE guild_id = %s
                        AND user_id = %s
                        AND dm_type = %s
                """, (
                    guild_id,
                    user_id,
                    dm_type
                ))

            await conn.commit()
            
        except Exception:
            await conn.rollback()
            raise

# ==================================================
# DELETE BY MESSAGE ID
# ==================================================
async def delete_dm_message_by_id(
    message_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    DELETE FROM dm_message_db
                    WHERE message_id = %s
                """, (
                    message_id,
                ))

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise

# ==================================================
# CHECK EXISTS
# ==================================================
async def dm_message_exists(
    guild_id: int,
    user_id: int,
    dm_type: str
) -> bool:

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT 1
                FROM dm_message_db
                WHERE guild_id = %s
                    AND user_id = %s
                    AND dm_type = %s
                LIMIT 1
            """, (
                guild_id,
                user_id,
                dm_type
            ))

            row = await cursor.fetchone()

    return row is not None


# ==================================================
# GET ALL DM MESSAGES
# ==================================================
async def get_all_dm_messages(
    guild_id: int
):

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute("""
                SELECT
                    guild_id,
                    user_id,
                    dm_type,
                    message_id
                FROM dm_message_db
                WHERE guild_id = %s
            """, (
                guild_id,
            ))

            rows = await cursor.fetchall()

    return rows

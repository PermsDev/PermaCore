from database.database import get_pool
from asyncmy.cursors import DictCursor

# ==================================================
# CREATE FEEDBACK
# ==================================================
async def create_feedback(
    message_id: int,
    guild_id: int,
    channel_id: int,
    category: str,
    user_id: int,
    username: str,
    feedback: str,
    sent_at
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                INSERT INTO feedback_db (
                    message_id,
                    guild_id,
                    channel_id,
                    category,
                    user_id,
                    username,
                    feedback,
                    sent_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                message_id,
                guild_id,
                channel_id,
                category,
                user_id,
                username,
                feedback,
                sent_at
            ))

        await conn.commit()


# ==================================================
# REPLY FEEDBACK
# ==================================================
async def reply_feedback(
    message_id: int,
    admin_id: int,
    admin_name: str,
    reply: str,
    replied_at
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                UPDATE feedback_db
                SET
                    admin_id = %s,
                    admin_name = %s,
                    reply = %s,
                    replied_at = %s
                WHERE message_id = %s
            """, (
                admin_id,
                admin_name,
                reply,
                replied_at,
                message_id
            ))

        await conn.commit()


# ==================================================
# GET FEEDBACK
# ==================================================
async def get_feedback(
    message_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute("""
                SELECT *
                FROM feedback_db
                WHERE message_id = %s
            """, (
                message_id,
            ))

            result = await cursor.fetchone()

    return result


# ==================================================
# GET GUILD FEEDBACKS
# ==================================================
async def get_guild_feedbacks(
    guild_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute("""
                SELECT *
                FROM feedback_db
                WHERE guild_id = %s
                ORDER BY sent_at DESC
            """, (
                guild_id,
            ))

            result = await cursor.fetchall()

    return result


# ==================================================
# DELETE FEEDBACK
# ==================================================
async def delete_feedback(
    message_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                DELETE FROM feedback_db
                WHERE message_id = %s
            """, (
                message_id,
            ))

        await conn.commit()


# ==================================================
# GET PENDING FEEDBACKS
# ==================================================
async def get_pending_feedbacks():
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute("""
                SELECT message_id
                FROM feedback_db
                WHERE reply IS NULL
            """)

            result = await cursor.fetchall()

    return result
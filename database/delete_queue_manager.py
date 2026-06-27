from database.database import get_pool
from asyncmy.cursors import DictCursor


# ==================================================
# CREATE / UPDATE QUEUE
# ==================================================
async def upsert_delete_queue(
    channel_id: int,
    message_id: int,
    delete_at: float
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                INSERT INTO delete_queue_db (
                    channel_id,
                    message_id,
                    delete_at
                )
                VALUES (%s, %s, %s)

                ON DUPLICATE KEY UPDATE
                    channel_id = VALUES(channel_id),
                    delete_at = VALUES(delete_at)
            """, (
                channel_id,
                message_id,
                delete_at
            ))

        await conn.commit()


# ==================================================
# GET ALL QUEUE
# ==================================================
async def get_delete_queue():
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute("""
                SELECT *
                FROM delete_queue_db
                ORDER BY delete_at ASC
            """)

            result = await cursor.fetchall()

    return result


# ==================================================
# GET EXPIRED QUEUE
# ==================================================
async def get_expired_delete_queue(
    current_time: float
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute("""
                SELECT *
                FROM delete_queue_db
                WHERE delete_at <= %s
                ORDER BY delete_at ASC
            """, (
                current_time,
            ))

            result = await cursor.fetchall()

    return result


# ==================================================
# DELETE QUEUE ITEM
# ==================================================
async def delete_queue_item(
    message_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                DELETE FROM delete_queue_db
                WHERE message_id = %s
            """, (
                message_id,
            ))

        await conn.commit()


# ==================================================
# CLEAR ALL QUEUE
# ==================================================
async def clear_delete_queue():
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                DELETE FROM delete_queue_db
            """)

        await conn.commit()
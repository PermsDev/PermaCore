from database.database import get_main_pool as get_pool


async def ensure_user_exists(
    user_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO user_db (
                        user_id
                    )
                    VALUES (%s)
                    ON DUPLICATE KEY UPDATE
                        user_id = user_id
                """, (
                    user_id,
                ))

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise


async def ensure_users_exist(
    user_ids: list[int]
):
    if not user_ids:
        return

    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:

                values = [
                    (user_id,)
                    for user_id in user_ids
                ]

                await cursor.executemany("""
                    INSERT INTO user_db (
                        user_id
                    )
                    VALUES (%s)
                    ON DUPLICATE KEY UPDATE
                        user_id = user_id
                """, values)

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise


async def user_exists(
    user_id: int
) -> bool:
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT 1
                FROM user_db
                WHERE user_id = %s
                LIMIT 1
            """, (
                user_id,
            ))

            return await cursor.fetchone() is not None
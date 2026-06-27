from database.database import get_pool


async def ensure_user_exists(
    guild_id: int,
    user_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO user_db (
                        user_id,
                        guild_id,
                        nickname,
                        joined_at
                    )
                    VALUES (%s, %s, NULL, NULL)
                    ON DUPLICATE KEY UPDATE
                        user_id = user_id
                """, (
                    user_id,
                    guild_id
                ))

            await conn.commit()
            
        except Exception:
            await conn.rollback()
            raise
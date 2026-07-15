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
        
async def get_all_users(guild_id: int):
    print("[DB] Acquire connection")

    pool = get_pool()

    async with pool.acquire() as conn:
        print("[DB] Connection acquired")

        async with conn.cursor() as cursor:
            print("[DB] Execute query")

            await cursor.execute("""
                SELECT
                    user_id,
                    guild_id
                FROM user_db
                WHERE guild_id=%s
            """, (guild_id,))

            print("[DB] Fetch all")

            rows = await cursor.fetchall()

            print(f"[DB] Loaded {len(rows)} rows")

            return rows
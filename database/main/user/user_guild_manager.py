from database.database import get_main_pool as get_pool


async def ensure_user_guild_exists(
    user_id: int,
    guild_id: int
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

                await cursor.execute("""
                    INSERT INTO user_guild_db (
                        user_id,
                        guild_id,
                        joined_at
                    )
                    VALUES (%s, %s, NULL)
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


async def ensure_users_guild_exist(
    guild_id: int,
    user_ids: list[int]
):
    if not user_ids:
        return

    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:

                user_values = [
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
                """, user_values)

                guild_values = [
                    (
                        user_id,
                        guild_id
                    )
                    for user_id in user_ids
                ]

                await cursor.executemany("""
                    INSERT INTO user_guild_db (
                        user_id,
                        guild_id,
                        joined_at
                    )
                    VALUES (%s, %s, NULL)
                    ON DUPLICATE KEY UPDATE
                        user_id = user_id
                """, guild_values)

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise


async def sync_users(guild_id: int, members: list):
    if not members:
        return

    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:

                user_values = [
                    (member.id,)
                    for member in members
                ]

                await cursor.executemany("""
                    INSERT INTO user_db (
                        user_id
                    )
                    VALUES (%s)
                    ON DUPLICATE KEY UPDATE
                        user_id = user_id
                """, user_values)

                guild_values = [
                    (
                        member.id,
                        guild_id,
                        member.joined_at.replace(tzinfo=None)
                        if member.joined_at
                        else None
                    )
                    for member in members
                ]

                await cursor.executemany("""
                    INSERT INTO user_guild_db (
                        user_id,
                        guild_id,
                        joined_at
                    )
                    VALUES (%s, %s, %s) 
                    ON DUPLICATE KEY UPDATE
                        joined_at = VALUES(joined_at)
                """, guild_values)

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise


async def get_all_users(guild_id: int):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    user_id,
                    guild_id,
                    joined_at
                FROM user_guild_db
                WHERE guild_id = %s
            """, (
                guild_id,
            ))

            return await cursor.fetchall()
from database.database import get_main_pool as get_pool


async def create_member(
    user_id: int,
    nickname: str
):
    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:

                await cursor.execute("""
                    INSERT INTO member_db (
                        user_id,
                        nickname
                    )
                    VALUES (%s, %s)
                """, (
                    user_id,
                    nickname
                ))

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise


async def update_nickname(
    user_id: int,
    nickname: str
):
    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:

                await cursor.execute("""
                    UPDATE member_db
                    SET nickname = %s
                    WHERE user_id = %s
                """, (
                    nickname,
                    user_id
                ))

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise


async def get_nickname(
    user_id: int
) -> str | None:
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT nickname
                FROM member_db
                WHERE user_id = %s
            """, (
                user_id,
            ))

            row = await cursor.fetchone()

            if row is None:
                return None

            return row[0]


async def get_member(
    user_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    user_id,
                    nickname,
                    created_at,
                    updated_at
                FROM member_db
                WHERE user_id = %s
            """, (
                user_id,
            ))

            return await cursor.fetchone()


async def member_exists(
    user_id: int
) -> bool:
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT 1
                FROM member_db
                WHERE user_id = %s
                LIMIT 1
            """)

            return await cursor.fetchone() is not None
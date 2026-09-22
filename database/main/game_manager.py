from database.database import get_main_pool as get_pool


async def get_user_id_by_game_value(
    game_key: str,
    value: str
) -> int | None:

    pool = get_pool()

    query = """
        SELECT user_id
        FROM game_db
        WHERE game_key = %s
          AND value = %s
        LIMIT 1
    """

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                query,
                (game_key, value)
            )

            row = await cursor.fetchone()

            if not row:
                return None

            return row[0]
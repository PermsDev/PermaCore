from database.database import get_guild_pool as get_pool
from asyncmy.cursors import DictCursor


async def get_all_series() -> list[dict]:
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:
            await cursor.execute(
                """
                SELECT
                    series_id,
                    series_name,
                    start_date,
                    end_date,
                    status
                FROM event_clash_series
                ORDER BY start_date DESC
                """
            )

            rows = await cursor.fetchall()

    return rows


async def get_series(series_id: int) -> dict | None:
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:
            await cursor.execute(
                """
                SELECT
                    series_id,
                    series_name,
                    start_date,
                    end_date,
                    status
                FROM event_clash_series
                WHERE series_id = %s
                LIMIT 1
                """,
                (
                    series_id,
                )
            )

            row = await cursor.fetchone()

    return row
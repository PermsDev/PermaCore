from datetime import date

from database.database import get_guild_pool as get_pool


async def get_current_top_clash() -> list[dict]:
    today = date.today()

    if today.month >= 7:
        series_start = date(today.year, 7, 1)
        series_end = date(today.year + 1, 6, 30)
    else:
        series_start = date(today.year - 1, 7, 1)
        series_end = date(today.year, 6, 30)

    pool = get_pool()

    async with pool.acquire() as conn:

        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    series_id
                FROM event_clash_series
                WHERE start_date <= %s
                    AND end_date >= %s
                ORDER BY series_id DESC
                LIMIT 1
                """,
                (
                    today,
                    today,
                )
            )

            series = await cursor.fetchone()

            if series is None:
                return []

            series_id = series[0]

            await cursor.execute(
                """
                SELECT
                    ecr.rank_position,
                    ecr.growid,
                    ecr.user_id,
                    gd.value
                FROM event_clash_result ecr
                LEFT JOIN perma_main.game_db gd
                    ON gd.user_id = ecr.user_id
                    AND gd.game_key = 'growtopia'
                INNER JOIN event_clash ec
                    ON ec.clash_id = ecr.clash_id
                WHERE ec.series_id = %s
                    AND ec.clash_month = %s
                    AND ec.clash_year = %s
                ORDER BY ecr.rank_position ASC
                """,
                (
                    series_id,
                    today.month,
                    today.year,
                )
            )

            rows = await cursor.fetchall()

    results = [
        {
            "rank_position": row[0],
            "growid": row[1] or row[3],
            "user_id": row[2],
        }
        for row in rows
    ]

    return results
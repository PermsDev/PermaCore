from datetime import date

from database.database import get_guild_pool as get_pool


async def get_top_total_score(
    limit: int = 5
) -> list[dict]:

    pool = get_pool()

    async with pool.acquire() as conn:

        async with conn.cursor() as cursor:

            today = date.today()

            await cursor.execute(
                """
                SELECT
                    ecr.user_id,
                    COALESCE(
                        MAX(gdb.value),
                        MAX(ecr.growid)
                    ) AS growid,
                    SUM(ecp.points) AS total_points,
                    ecs.series_id,
                    ecs.series_name
                FROM event_clash_result ecr
                INNER JOIN event_clash ec
                    ON ec.clash_id = ecr.clash_id
                INNER JOIN event_clash_series ecs
                    ON ecs.series_id = ec.series_id
                INNER JOIN event_clash_point ecp
                    ON ecp.rank_position = ecr.rank_position
                LEFT JOIN perma_main.game_db gdb
                    ON gdb.user_id = ecr.user_id
                    AND gdb.game_key = 'growtopia'
                WHERE ecs.series_id = (
                    SELECT series_id
                    FROM event_clash_series
                    WHERE start_date <= %s
                        AND end_date >= %s
                        AND status = 'active'
                    ORDER BY series_id DESC
                    LIMIT 1
                )
                GROUP BY
                    ecr.user_id,
                    ecr.growid,
                    ecs.series_id,
                    ecs.series_name
                ORDER BY
                    total_points DESC
                LIMIT %s
                """,
                (
                    today,
                    today,
                    limit,
                )
            )

            rows = await cursor.fetchall()

            return [
                {
                    "user_id": row[0],
                    "growid": row[1],
                    "total_points": row[2],
                    "series_id": row[3],
                    "series_name": row[4],
                }
                for row in rows
            ]


async def get_top_monthly_score(
    limit: int = 5
) -> list[dict]:

    pool = get_pool()

    async with pool.acquire() as conn:

        async with conn.cursor() as cursor:

            today = date.today()

            await cursor.execute(
                """
                SELECT
                    ec.clash_id,
                    ecs.series_id,
                    ecs.series_name
                FROM event_clash ec
                INNER JOIN event_clash_series ecs
                    ON ecs.series_id = ec.series_id
                WHERE ec.clash_month = %s
                    AND ec.clash_year = %s
                    AND ecs.start_date <= %s
                    AND ecs.end_date >= %s
                ORDER BY
                    ec.clash_id DESC
                LIMIT 1
                """,
                (
                    today.month,
                    today.year,
                    today,
                    today,
                )
            )

            clash = await cursor.fetchone()

            if clash is None:
                return []

            clash_id = clash[0]
            series_id = clash[1]
            series_name = clash[2]

            await cursor.execute(
                """
                SELECT
                    ecr.user_id,
                    COALESCE(
                        gdb.value,
                        ecr.growid
                    ) AS growid,
                    ecr.rank_position,
                    ecp.points
                FROM event_clash_result ecr
                INNER JOIN event_clash_point ecp
                    ON ecp.rank_position = ecr.rank_position
                LEFT JOIN perma_main.game_db gdb
                    ON gdb.user_id = ecr.user_id
                    AND gdb.game_key = 'growtopia'
                WHERE ecr.clash_id = %s
                ORDER BY
                    ecr.rank_position ASC
                LIMIT %s
                """,
                (
                    clash_id,
                    limit,
                )
            )

            rows = await cursor.fetchall()

            return [
                {
                    "user_id": row[0],
                    "growid": row[1],
                    "rank_position": row[2],
                    "points": row[3],
                    "series_id": series_id,
                    "series_name": series_name,
                }
                for row in rows
            ]
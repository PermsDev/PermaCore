from datetime import date

from database.database import get_guild_pool as get_pool

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
                    ecs.series_id,
                    ecs.series_name,
                    ecs.start_date,
                    ecs.end_date
                FROM event_clash_series ecs
                WHERE ecs.start_date <= %s
                    AND ecs.end_date >= %s
                    AND ecs.status = 'active'
                ORDER BY
                    ecs.series_id DESC
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
            series_name = series[1]
            start_date = series[2]
            end_date = series[3]

            await cursor.execute(
                """
                SELECT
                    ecr.user_id,
                    COALESCE(
                        gdb.value,
                        MAX(ecr.growid)
                    ) AS growid,
                    SUM(ecp.points) AS total_points
                FROM event_clash_result ecr
                INNER JOIN event_clash ec
                    ON ec.clash_id = ecr.clash_id
                INNER JOIN event_clash_point ecp
                    ON ecp.rank_position = ecr.rank_position
                LEFT JOIN perma_main.game_db gdb
                    ON gdb.user_id = ecr.user_id
                    AND gdb.game_key = 'growtopia'
                WHERE ec.series_id = %s
                GROUP BY
                    ecr.user_id,
                    gdb.value
                ORDER BY
                    total_points DESC
                """,
                (
                    series_id,
                )
            )

            players = await cursor.fetchall()

            if not players:
                return []

            await cursor.execute(
                """
                SELECT
                    ecr.user_id,
                    ec.clash_month,
                    ec.clash_year,
                    ecr.rank_position,
                    ecp.points
                FROM event_clash_result ecr
                INNER JOIN event_clash ec
                    ON ec.clash_id = ecr.clash_id
                INNER JOIN event_clash_point ecp
                    ON ecp.rank_position = ecr.rank_position
                WHERE ec.series_id = %s
                ORDER BY
                    ec.clash_year ASC,
                    ec.clash_month ASC,
                    ecr.user_id ASC
                """,
                (
                    series_id,
                )
            )

            clash_rows = await cursor.fetchall()

            clash_map = {}

            for row in clash_rows:

                user_id = row[0]
                clash_month = row[1]
                clash_year = row[2]
                rank_position = row[3]
                points = row[4]

                clash_key = (
                    clash_year,
                    clash_month
                )

                if user_id not in clash_map:
                    clash_map[user_id] = {}

                clash_map[user_id][clash_key] = {
                    "rank_position": rank_position,
                    "points": points
                }

            clash_keys = sorted({
                (
                    row[1],
                    row[2]
                )
                for row in clash_rows
            })

            clash_keys = sorted(
                clash_keys,
                key=lambda value: (
                    value[1],
                    value[0]
                )
            )

            def get_rank_key(user_id):

                result = []

                for clash_key in reversed(clash_keys):

                    clash = clash_map.get(
                        user_id,
                        {}
                    ).get(clash_key)

                    if clash is None:
                        result.append(
                            (
                                0,
                                6
                            )
                        )
                    else:
                        result.append(
                            (
                                clash["points"],
                                clash["rank_position"]
                            )
                        )

                return result

            players.sort(
                key=lambda row: (
                    -row[2],
                    [
                        (
                            -points,
                            rank
                        )
                        for points, rank in get_rank_key(row[0])
                    ]
                )
            )

            players = players[:limit]

            return [
                {
                    "user_id": row[0],
                    "growid": row[1],
                    "total_points": row[2],
                    "series_id": series_id,
                    "series_name": series_name,
                    "start_date": start_date,
                    "end_date": end_date,
                }
                for row in players
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
                    ecs.series_name,
                    ecs.start_date,
                    ecs.end_date
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
            start_date = clash[3]
            end_date = clash[4]

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
                    "start_date": start_date,
                    "end_date": end_date,
                }
                for row in rows
            ]
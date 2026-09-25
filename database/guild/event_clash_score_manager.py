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
                    ecr.growid,
                    gdb.value,
                    ecp.points
                FROM event_clash_result ecr
                INNER JOIN event_clash ec
                    ON ec.clash_id = ecr.clash_id
                INNER JOIN event_clash_point ecp
                    ON ecp.rank_position = ecr.rank_position
                LEFT JOIN perma_main.game_db gdb
                    ON gdb.user_id = ecr.user_id
                    AND gdb.game_key = 'growtopia'
                WHERE ec.series_id = %s
                ORDER BY
                    ec.clash_year ASC,
                    ec.clash_month ASC
                """,
                (
                    series_id,
                )
            )

            rows = await cursor.fetchall()

            if not rows:
                return []

            players = {}

            clash_map = {}

            clash_keys = set()

            for row in rows:

                user_id = row[0]
                entered_growid = row[1]
                database_growid = row[2]
                points = row[3]

                identity = (
                    ("user", user_id)
                    if user_id is not None
                    else ("growid", entered_growid)
                )

                if identity not in players:
                    players[identity] = {
                        "user_id": user_id,
                        "growid": (
                            database_growid
                            or entered_growid
                        ),
                        "total_points": 0
                    }

                players[identity]["total_points"] += points

            await cursor.execute(
                """
                SELECT
                    ecr.user_id,
                    ecr.growid,
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
                    ec.clash_month ASC
                """,
                (
                    series_id,
                )
            )

            clash_rows = await cursor.fetchall()

            for row in clash_rows:

                user_id = row[0]
                growid = row[1]
                clash_month = row[2]
                clash_year = row[3]
                rank_position = row[4]
                points = row[5]

                identity = (
                    ("user", user_id)
                    if user_id is not None
                    else ("growid", growid)
                )

                clash_key = (
                    clash_year,
                    clash_month
                )

                clash_keys.add(clash_key)

                if identity not in clash_map:
                    clash_map[identity] = {}

                clash_map[identity][clash_key] = {
                    "rank_position": rank_position,
                    "points": points
                }

            clash_keys = sorted(clash_keys)

            def get_rank_key(identity):

                result = []

                user_clashes = clash_map.get(
                    identity,
                    {}
                )

                for clash_key in clash_keys:

                    clash = user_clashes.get(
                        clash_key
                    )

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

            player_list = list(
                players.values()
            )

            identity_map = {
                identity: data
                for identity, data in players.items()
            }

            player_list = sorted(
                identity_map.items(),
                key=lambda item: (
                    -item[1]["total_points"],
                    [
                        (
                            -points,
                            rank
                        )
                        for points, rank in get_rank_key(item[0])
                    ]
                )
            )

            player_list = player_list[:limit]

            return [
                {
                    "user_id": data["user_id"],
                    "growid": data["growid"],
                    "total_points": data["total_points"],
                    "series_id": series_id,
                    "series_name": series_name,
                    "start_date": start_date,
                    "end_date": end_date,
                }
                for identity, data in player_list
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
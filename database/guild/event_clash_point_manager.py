from database.database import get_guild_pool as get_pool

async def get_clash_points():

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    rank_position,
                    points
                FROM event_clash_point
                ORDER BY rank_position ASC
                """
            )

            rows = await cursor.fetchall()

            return [
                {
                    "rank_position": row[0],
                    "points": row[1]
                }
                for row in rows
            ]


async def get_clash_point(rank_position: int):

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT points
                FROM event_clash_point
                WHERE rank_position = %s
                LIMIT 1
                """,
                (rank_position,)
            )

            row = await cursor.fetchone()

            return row[0] if row else None
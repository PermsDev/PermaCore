from database.database import get_main_pool as get_pool

# ==================================================
# USER PROFILE FOR MODAL
# ==================================================
async def get_user_profile_for_modal(
    guild_id: int,
    user_id: int
):
    main_pool = get_pool()

    async with main_pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    ug.user_id,
                    ug.guild_id,
                    m.nickname,
                    ug.joined_at
                FROM user_guild_db AS ug
                LEFT JOIN member_db AS m
                    ON m.user_id = ug.user_id
                WHERE ug.guild_id = %s
                AND ug.user_id = %s
            """, (
                guild_id,
                user_id
            ))

            row = await cursor.fetchone()

            if row is None:
                return {}

            profile = {
                "user_id": row[0],
                "guild_id": row[1],
                "nickname": row[2],
                "joined_at": row[3],
                "games": {}
            }

            await cursor.execute("""
                SELECT
                    game_key,
                    value
                FROM game_db
                WHERE user_id = %s
            """, (
                user_id,
            ))

            game_rows = await cursor.fetchall()

            for game_key, value in game_rows:
                profile["games"][game_key] = {
                    "value": value
                }

            return profile

from database.database import get_pool


# ==================================================
# GET ALL GUILD
# ==================================================
async def get_all_guild_ids() -> list[int]:
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT guild_id
                FROM guild_db
            """)

            rows = await cursor.fetchall()

    return [row[0] for row in rows]

# ==================================================
# ADD / UPDATE GUILD
# ==================================================
async def add_guild(
    guild_id: int,
    nama_guild: str
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                INSERT INTO guild_db (
                    guild_id,
                    nama_guild
                )
                VALUES (%s, %s)

                ON DUPLICATE KEY UPDATE
                    nama_guild = VALUES(nama_guild)
            """, (
                guild_id,
                nama_guild
            ))

        await conn.commit()


# ==================================================
# REMOVE GUILD
# ==================================================
async def remove_guild(
    guild_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                DELETE FROM guild_db
                WHERE guild_id = %s
            """, (
                guild_id,
            ))

        await conn.commit()
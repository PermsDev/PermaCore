from database.database import get_pool
from asyncmy.cursors import DictCursor

# ==================================================
# GET GUILD IDS
# ==================================================
async def get_guild_ids(
    guild_key: str
) -> list[int]:
    """
    Mengambil seluruh guild_id berdasarkan guild_key.
    """

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute("""
                SELECT guild_id
                FROM guild_key_db
                WHERE guild_key=%s
            """, (guild_key,))

            rows = await cursor.fetchall()

    return [
        row["guild_id"]
        for row in rows
    ]
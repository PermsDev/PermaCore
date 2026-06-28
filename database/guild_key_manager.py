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
    
# ==================================================
# CHECK MAIN GUILD
# ==================================================
async def is_main_guild(guild_id: int) -> bool:
    """
    Mengembalikan True jika guild memiliki guild_key = 'Main'.
    """

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute("""
                SELECT 1
                FROM guild_key_db
                WHERE guild_id = %s
                AND guild_key = 'Main'
                LIMIT 1
            """, (guild_id,))

            row = await cursor.fetchone()

    return row is not None
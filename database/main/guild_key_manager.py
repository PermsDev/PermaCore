from database.database import get_main_pool as get_pool
from asyncmy.cursors import DictCursor

# ==================================================
# GET GUILD IDS BY KEY
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
                WHERE guild_key = %s
                ORDER BY guild_id
            """, (
                guild_key,
            ))

            rows = await cursor.fetchall()

    return [
        row["guild_id"]
        for row in rows
    ]


# ==================================================
# GET GUILD KEYS
# ==================================================
async def get_guild_keys(
    guild_id: int
) -> list[str]:
    """
    Mengambil seluruh guild_key yang dimiliki guild.
    """

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute("""
                SELECT guild_key
                FROM guild_key_db
                WHERE guild_id = %s
                ORDER BY guild_key
            """, (
                guild_id,
            ))

            rows = await cursor.fetchall()

    return [
        row["guild_key"]
        for row in rows
    ]


# ==================================================
# CHECK GUILD KEY
# ==================================================
async def has_guild_key(
    guild_id: int,
    guild_key: str
) -> bool:
    """
    Mengecek apakah guild memiliki guild_key tertentu.
    """

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT 1
                FROM guild_key_db
                WHERE guild_id = %s
                  AND guild_key = %s
                LIMIT 1
            """, (
                guild_id,
                guild_key
            ))

            return await cursor.fetchone() is not None


# ==================================================
# CHECK MAIN GUILD
# ==================================================
async def is_main_guild(
    guild_id: int
) -> bool:
    """
    Mengecek apakah guild memiliki guild_key = 'Main'.
    """

    return await has_guild_key(
        guild_id,
        "Main"
    )


# ==================================================
# ADD GUILD KEY
# ==================================================
async def add_guild_key(
    guild_key: str,
    guild_id: int
):
    """
    Menambahkan guild_key ke guild.
    """

    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:

                await cursor.execute("""
                    INSERT IGNORE INTO guild_key_db (
                        guild_key,
                        guild_id
                    )
                    VALUES (%s, %s)
                """, (
                    guild_key,
                    guild_id
                ))

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise


# ==================================================
# REMOVE GUILD KEY
# ==================================================
async def remove_guild_key(
    guild_key: str,
    guild_id: int
):
    """
    Menghapus guild_key dari guild.
    """

    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:

                await cursor.execute("""
                    DELETE FROM guild_key_db
                    WHERE guild_key = %s
                      AND guild_id = %s
                """, (
                    guild_key,
                    guild_id
                ))

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise


# ==================================================
# GET ALL GUILD KEYS
# ==================================================
async def get_all_guild_keys() -> list[dict]:
    """
    Mengambil seluruh relasi guild_key dan guild.
    """

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute("""
                SELECT
                    gk.guild_key,
                    gk.guild_id,
                    g.guild_name
                FROM guild_key_db gk

                INNER JOIN guild_db g
                    ON g.guild_id = gk.guild_id

                ORDER BY
                    gk.guild_key,
                    g.guild_name
            """)

            return await cursor.fetchall()
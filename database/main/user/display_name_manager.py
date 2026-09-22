from database.database import get_main_pool as get_pool


# ======================
# GET DISPLAY SOURCE
# ======================

async def get_display_source(
    guild_id: int,
    user_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    display_source
                FROM user_display_name_settings
                WHERE guild_id = %s
                    AND user_id = %s
                LIMIT 1
                """,
                (
                    guild_id,
                    user_id
                )
            )

            row = await cursor.fetchone()

    if not row:
        return None

    return row[0]


# ======================
# GET OR CREATE DEFAULT
# ======================

async def get_or_create_display_source(
    guild_id: int,
    user_id: int
):
    source = await get_display_source(
        guild_id,
        user_id
    )

    # User sudah memiliki pilihan
    if source:
        return source

    # User belum memiliki pilihan
    await set_display_source(
        guild_id=guild_id,
        user_id=user_id,
        display_source="nickname"
    )

    return "nickname"


# ======================
# SET DISPLAY SOURCE
# ======================

async def set_display_source(
    guild_id: int,
    user_id: int,
    display_source: str
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                INSERT INTO user_display_name_settings (
                    guild_id,
                    user_id,
                    display_source
                )
                VALUES (%s, %s, %s) 

                ON DUPLICATE KEY UPDATE
                    display_source = VALUES(display_source)
                """,
                (
                    guild_id,
                    user_id,
                    display_source
                )
            )

        await conn.commit()


# ======================
# DELETE DISPLAY SETTING
# ======================

async def delete_display_source(
    guild_id: int,
    user_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                DELETE FROM user_display_name_settings
                WHERE guild_id = %s
                    AND user_id = %s
                """,
                (
                    guild_id,
                    user_id
                )
            )

        await conn.commit()
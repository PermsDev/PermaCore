from database.database import get_core_pool as get_pool
from asyncmy.cursors import DictCursor


# ==================================================
# CACHE EMOJI
# ==================================================

EMOJIS = {}


# ==================================================
# LOAD SEMUA EMOJI
# ==================================================

async def load_emojis():

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute("""
                SELECT
                    emoji_key,
                    emoji_id,
                    animated
                FROM emoji_db
            """)

            rows = await cursor.fetchall()

    EMOJIS.clear()

    for row in rows:

        EMOJIS[row["emoji_key"]] = {
            "emoji_id": row["emoji_id"],
            "animated": bool(row["animated"])
        }


# ==================================================
# RELOAD CACHE
# ==================================================

async def reload_emojis():

    await load_emojis()


# ==================================================
# GET SEMUA EMOJI
# ==================================================

def get_emojis():

    return EMOJIS.copy()


# ==================================================
# GET EMOJI ID
# ==================================================

def get_emoji_id(
    emoji_key: str
):

    emoji = EMOJIS.get(emoji_key)

    if not emoji:
        return None

    return emoji["emoji_id"]


# ==================================================
# GET FORMAT EMOJI DISCORD
# ==================================================

def get_emoji(
    emoji_key: str,
    default: str = "🎯"
):

    emoji = EMOJIS.get(emoji_key)

    if not emoji:
        return default

    emoji_id = emoji["emoji_id"]
    animated = emoji["animated"]

    if animated:
        return f"<a:{emoji_key}:{emoji_id}>"

    return f"<:{emoji_key}:{emoji_id}>"


# ==================================================
# TAMBAH / UPDATE EMOJI
# ==================================================

async def set_emoji(
    emoji_key: str,
    emoji_id: int,
    animated: bool
):

    pool = get_pool()

    async with pool.acquire() as conn:

        try:

            async with conn.cursor() as cursor:

                await cursor.execute("""
                    INSERT INTO emoji_db (
                        emoji_key,
                        emoji_id,
                        animated
                    )
                    VALUES (%s, %s, %s) AS new

                    ON DUPLICATE KEY UPDATE
                        emoji_id = new.emoji_id,
                        animated = new.animated
                """, (
                    emoji_key,
                    emoji_id,
                    animated
                ))

            await conn.commit()

        except Exception:

            await conn.rollback()
            raise

    EMOJIS[emoji_key] = {
        "emoji_id": emoji_id,
        "animated": animated
    }


# ==================================================
# HAPUS EMOJI
# ==================================================

async def delete_emoji(
    emoji_key: str
):

    pool = get_pool()

    async with pool.acquire() as conn:

        try:

            async with conn.cursor() as cursor:

                await cursor.execute("""
                    DELETE FROM emoji_db
                    WHERE emoji_key = %s
                """, (
                    emoji_key,
                ))

            await conn.commit()

        except Exception:

            await conn.rollback()
            raise

    EMOJIS.pop(
        emoji_key,
        None
    )
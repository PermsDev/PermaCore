# database/executive/executive_manager.py

from database.database import get_core_pool as get_pool


# ============================================================
# EXECUTIVE TYPE
# ============================================================

async def get_executive_types():
    """
    Mengambil semua executive type.
    """

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT
                    id,
                    executive_key,
                    name
                FROM executive_type_db
                ORDER BY id ASC
            """)

            rows = await cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "executive_key": row[1],
                    "name": row[2]
                }
                for row in rows
            ]


async def get_executive_type(executive_key: str):
    """
    Mengambil satu executive type berdasarkan executive_key.

    Contoh:
        get_executive_type("guild")
    """

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT
                    id,
                    executive_key,
                    name
                FROM executive_type_db
                WHERE executive_key = %s
                LIMIT 1
            """, (executive_key,))

            row = await cursor.fetchone()

            if not row:
                return None

            return {
                "id": row[0],
                "executive_key": row[1],
                "name": row[2]
            }


# ============================================================
# EXECUTIVE SECTION KEY
# ============================================================

async def get_section_keys():
    """
    Mengambil semua section key.
    """

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT
                    id,
                    section_key,
                    name
                FROM executive_section_key_db
                ORDER BY id ASC
            """)

            rows = await cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "section_key": row[1],
                    "name": row[2]
                }
                for row in rows
            ]


async def get_section_key(section_key: str):
    """
    Mengambil satu section key berdasarkan section_key.

    Contoh:
        get_section_key("tugas")
    """

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT
                    id,
                    section_key,
                    name
                FROM executive_section_key_db
                WHERE section_key = %s
                LIMIT 1
            """, (section_key,))

            row = await cursor.fetchone()

            if not row:
                return None

            return {
                "id": row[0],
                "section_key": row[1],
                "name": row[2]
            }


# ============================================================
# EXECUTIVE SECTION
# ============================================================

async def get_executive_sections(executive_type_id: int):
    """
    Mengambil semua section berdasarkan executive_type_id.

    Mengembalikan:
        id
        executive_type_id
        section_key_id
        section_key
        section_name
        emoji_key
        description
    """

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT
                    s.id,
                    s.executive_type_id,
                    s.section_key_id,
                    sk.section_key,
                    sk.name AS section_name,
                    s.emoji_key,
                    s.description
                FROM executive_section_db AS s

                INNER JOIN executive_section_key_db AS sk
                    ON sk.id = s.section_key_id

                WHERE s.executive_type_id = %s

                ORDER BY s.section_key_id ASC
            """, (executive_type_id,))

            rows = await cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "executive_type_id": row[1],
                    "section_key_id": row[2],
                    "section_key": row[3],
                    "section_name": row[4],
                    "emoji_key": row[5],
                    "description": row[6]
                }
                for row in rows
            ]


async def get_executive_section(
    executive_type_id: int,
    section_key: str
):
    """
    Mengambil satu section berdasarkan:

        executive_type_id
        section_key

    Contoh:
        get_executive_section(1, "tugas")
    """

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT
                    s.id,
                    s.executive_type_id,
                    s.section_key_id,
                    sk.section_key,
                    sk.name AS section_name,
                    s.emoji_key,
                    s.description
                FROM executive_section_db AS s

                INNER JOIN executive_section_key_db AS sk
                    ON sk.id = s.section_key_id

                WHERE
                    s.executive_type_id = %s
                    AND sk.section_key = %s

                LIMIT 1
            """, (
                executive_type_id,
                section_key
            ))

            row = await cursor.fetchone()

            if not row:
                return None

            return {
                "id": row[0],
                "executive_type_id": row[1],
                "section_key_id": row[2],
                "section_key": row[3],
                "section_name": row[4],
                "emoji_key": row[5],
                "description": row[6]
            }


# ============================================================
# EXECUTIVE DATA
# ============================================================

async def get_executive(executive_key: str):
    """
    Mengambil executive type beserta seluruh section-nya.

    Contoh:
        get_executive("guild")
    """

    executive_type = await get_executive_type(
        executive_key
    )

    if not executive_type:
        return None

    sections = await get_executive_sections(
        executive_type["id"]
    )

    return {
        "id": executive_type["id"],
        "executive_key": executive_type["executive_key"],
        "name": executive_type["name"],
        "sections": sections
    }
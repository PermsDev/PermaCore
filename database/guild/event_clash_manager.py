from datetime import date

from database.database import get_guild_pool as get_pool


# =========================================================
# EVENT CLASH SERIES
# =========================================================

# ======================
# GET SERIES
# ======================

async def get_series(
    series_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    series_id,
                    series_name,
                    start_date,
                    end_date,
                    status,
                    created_at,
                    updated_at
                FROM event_clash_series
                WHERE series_id = %s
                LIMIT 1
                """,
                (
                    series_id,
                )
            )

            row = await cursor.fetchone()

    return row


# ======================
# GET SERIES BY NAME
# ======================

async def get_series_by_name(
    series_name: str
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    series_id,
                    series_name,
                    start_date,
                    end_date,
                    status,
                    created_at,
                    updated_at
                FROM event_clash_series
                WHERE series_name = %s
                LIMIT 1
                """,
                (
                    series_name,
                )
            )

            row = await cursor.fetchone()

    return row


# ======================
# GET SERIES BY DATE
# ======================

async def get_series_by_date(
    target_date: date
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    series_id,
                    series_name,
                    start_date,
                    end_date,
                    status,
                    created_at,
                    updated_at
                FROM event_clash_series
                WHERE start_date <= %s
                    AND end_date >= %s
                LIMIT 1
                """,
                (
                    target_date,
                    target_date,
                )
            )

            row = await cursor.fetchone()

    return row


# ======================
# GET ACTIVE SERIES
# ======================

async def get_active_series():
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    series_id,
                    series_name,
                    start_date,
                    end_date,
                    status,
                    created_at,
                    updated_at
                FROM event_clash_series
                WHERE status = 'active'
                ORDER BY series_id DESC
                LIMIT 1
                """
            )

            row = await cursor.fetchone()

    return row


# ======================
# GET ALL SERIES
# ======================

async def get_all_series():
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    series_id,
                    series_name,
                    start_date,
                    end_date,
                    status,
                    created_at,
                    updated_at
                FROM event_clash_series
                ORDER BY series_id DESC
                """
            )

            rows = await cursor.fetchall()

    return rows


# ======================
# ADD SERIES
# ======================

async def add_series(
    series_name: str,
    start_date,
    end_date,
    status: str = "upcoming"
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                INSERT INTO event_clash_series (
                    series_name,
                    start_date,
                    end_date,
                    status
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    series_name,
                    start_date,
                    end_date,
                    status,
                )
            )

            series_id = cursor.lastrowid

        await conn.commit()

    return series_id


# ======================
# EDIT SERIES
# ======================

async def edit_series(
    series_id: int,
    series_name: str,
    start_date,
    end_date,
    status: str
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                UPDATE event_clash_series
                SET
                    series_name = %s,
                    start_date = %s,
                    end_date = %s,
                    status = %s
                WHERE series_id = %s
                """,
                (
                    series_name,
                    start_date,
                    end_date,
                    status,
                    series_id,
                )
            )

        await conn.commit()


# =========================================================
# EVENT CLASH
# =========================================================

# ======================
# GET CLASH
# ======================

async def get_clash(
    clash_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    clash_id,
                    series_id,
                    clash_month,
                    clash_year,
                    event_date,
                    created_at
                FROM event_clash
                WHERE clash_id = %s
                LIMIT 1
                """,
                (
                    clash_id,
                )
            )

            row = await cursor.fetchone()

    return row


# ======================
# GET CLASH BY MONTH
# ======================

async def get_clash_by_month(
    series_id: int,
    clash_month: int,
    clash_year: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    clash_id,
                    series_id,
                    clash_month,
                    clash_year,
                    event_date,
                    created_at
                FROM event_clash
                WHERE series_id = %s
                    AND clash_month = %s
                    AND clash_year = %s
                LIMIT 1
                """,
                (
                    series_id,
                    clash_month,
                    clash_year,
                )
            )

            row = await cursor.fetchone()

    return row


# ======================
# GET SERIES CLASHES
# ======================

async def get_series_clashes(
    series_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    clash_id,
                    series_id,
                    clash_month,
                    clash_year,
                    event_date,
                    created_at
                FROM event_clash
                WHERE series_id = %s
                ORDER BY
                    clash_year ASC,
                    clash_month ASC
                """,
                (
                    series_id,
                )
            )

            rows = await cursor.fetchall()

    return rows


# ======================
# GET ALL CLASHES
# ======================

async def get_all_clashes():
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    clash_id,
                    series_id,
                    clash_month,
                    clash_year,
                    event_date,
                    created_at
                FROM event_clash
                ORDER BY
                    clash_year DESC,
                    clash_month DESC
                """
            )

            rows = await cursor.fetchall()

    return rows


# ======================
# ADD CLASH
# ======================

async def add_clash(
    series_id: int,
    clash_month: int,
    clash_year: int,
    event_date=None
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                INSERT INTO event_clash (
                    series_id,
                    clash_month,
                    clash_year,
                    event_date
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    series_id,
                    clash_month,
                    clash_year,
                    event_date,
                )
            )

            clash_id = cursor.lastrowid

        await conn.commit()

    return clash_id


# ======================
# EDIT CLASH
# ======================

async def edit_clash(
    clash_id: int,
    clash_month: int,
    clash_year: int,
    event_date=None
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                UPDATE event_clash
                SET
                    clash_month = %s,
                    clash_year = %s,
                    event_date = %s
                WHERE clash_id = %s
                """,
                (
                    clash_month,
                    clash_year,
                    event_date,
                    clash_id,
                )
            )

        await conn.commit()


# =========================================================
# EVENT CLASH RESULT
# =========================================================

# ======================
# GET RESULT
# ======================

async def get_result(
    result_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    result_id,
                    clash_id,
                    user_id,
                    growid,
                    rank_position,
                    created_at
                FROM event_clash_result
                WHERE result_id = %s
                LIMIT 1
                """,
                (
                    result_id,
                )
            )

            row = await cursor.fetchone()

    return row


# ======================
# GET CLASH RESULTS
# ======================

async def get_clash_results(
    clash_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    result_id,
                    clash_id,
                    user_id,
                    growid,
                    rank_position,
                    created_at
                FROM event_clash_result
                WHERE clash_id = %s
                ORDER BY rank_position ASC
                """,
                (
                    clash_id,
                )
            )

            rows = await cursor.fetchall()

    return rows


# ======================
# GET USER RESULT
# ======================

async def get_user_result(
    clash_id: int,
    user_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    result_id,
                    clash_id,
                    user_id,
                    growid,
                    rank_position,
                    created_at
                FROM event_clash_result
                WHERE clash_id = %s
                    AND user_id = %s
                LIMIT 1
                """,
                (
                    clash_id,
                    user_id,
                )
            )

            row = await cursor.fetchone()

    return row


# ======================
# GET RANK RESULT
# ======================

async def get_rank_result(
    clash_id: int,
    rank_position: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    result_id,
                    clash_id,
                    user_id,
                    growid,
                    rank_position,
                    created_at
                FROM event_clash_result
                WHERE clash_id = %s
                    AND rank_position = %s
                LIMIT 1
                """,
                (
                    clash_id,
                    rank_position,
                )
            )

            row = await cursor.fetchone()

    return row


# ======================
# ADD RESULT
# ======================

async def add_result(
    clash_id: int,
    user_id=None,
    growid: str = None,
    rank_position: int = 0
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                INSERT INTO event_clash_result (
                    clash_id,
                    user_id,
                    growid,
                    rank_position
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    clash_id,
                    user_id,
                    growid,
                    rank_position,
                )
            )

            result_id = cursor.lastrowid

        await conn.commit()

    return result_id


# ======================
# EDIT RESULT
# ======================

async def edit_result(
    result_id: int,
    user_id=None,
    growid: str = None,
    rank_position: int = 0
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                UPDATE event_clash_result
                SET
                    user_id = %s,
                    growid = %s,
                    rank_position = %s
                WHERE result_id = %s
                """,
                (
                    user_id,
                    growid,
                    rank_position,
                    result_id,
                )
            )

        await conn.commit()

# =========================================================
# STRUCTURE
# =========================================================

# SERIES
# ├── get_series()
# ├── get_series_by_name()
# ├── get_series_by_date()
# ├── get_active_series()
# ├── get_all_series()
# ├── add_series()
# └── edit_series()

# CLASH
# ├── get_clash()
# ├── get_clash_by_month()
# ├── get_series_clashes()
# ├── get_all_clashes()
# ├── add_clash()
# └── edit_clash()

# RESULT
# ├── get_result()
# ├── get_clash_results()
# ├── get_user_result()
# ├── get_rank_result()
# ├── add_result()
# └── edit_result()

# SAVE
# └── save_top_clash()
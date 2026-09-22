from database.database import get_guild_pool as get_pool


# =========================================================
# EVENT CLASH SEASON
# =========================================================

# ======================
# GET SEASON
# ======================

async def get_season(
    season_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    season_id,
                    season_name,
                    start_date,
                    end_date,
                    status,
                    created_at,
                    updated_at
                FROM event_clash_season
                WHERE season_id = %s
                LIMIT 1
                """,
                (
                    season_id,
                )
            )

            row = await cursor.fetchone()

    return row


# ======================
# GET SEASON BY NAME
# ======================

async def get_season_by_name(
    season_name: str
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    season_id,
                    season_name,
                    start_date,
                    end_date,
                    status,
                    created_at,
                    updated_at
                FROM event_clash_season
                WHERE season_name = %s
                LIMIT 1
                """,
                (
                    season_name,
                )
            )

            row = await cursor.fetchone()

    return row


# ======================
# GET ACTIVE SEASON
# ======================

async def get_active_season():
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    season_id,
                    season_name,
                    start_date,
                    end_date,
                    status,
                    created_at,
                    updated_at
                FROM event_clash_season
                WHERE status = 'active'
                ORDER BY season_id DESC
                LIMIT 1
                """
            )

            row = await cursor.fetchone()

    return row


# ======================
# GET ALL SEASONS
# ======================

async def get_all_seasons():
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    season_id,
                    season_name,
                    start_date,
                    end_date,
                    status,
                    created_at,
                    updated_at
                FROM event_clash_season
                ORDER BY season_id DESC
                """
            )

            rows = await cursor.fetchall()

    return rows


# ======================
# ADD SEASON
# ======================

async def add_season(
    season_name: str,
    start_date,
    end_date,
    status: str = "upcoming"
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                INSERT INTO event_clash_season (
                    season_name,
                    start_date,
                    end_date,
                    status
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    season_name,
                    start_date,
                    end_date,
                    status,
                )
            )

            season_id = cursor.lastrowid

        await conn.commit()

    return season_id


# ======================
# EDIT SEASON
# ======================

async def edit_season(
    season_id: int,
    season_name: str,
    start_date,
    end_date,
    status: str
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                UPDATE event_clash_season
                SET
                    season_name = %s,
                    start_date = %s,
                    end_date = %s,
                    status = %s
                WHERE season_id = %s
                """,
                (
                    season_name,
                    start_date,
                    end_date,
                    status,
                    season_id,
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
                    season_id,
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
    season_id: int,
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
                    season_id,
                    clash_month,
                    clash_year,
                    event_date,
                    created_at
                FROM event_clash
                WHERE season_id = %s
                    AND clash_month = %s
                    AND clash_year = %s
                LIMIT 1
                """,
                (
                    season_id,
                    clash_month,
                    clash_year,
                )
            )

            row = await cursor.fetchone()

    return row


# ======================
# GET SEASON CLASHES
# ======================

async def get_season_clashes(
    season_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    clash_id,
                    season_id,
                    clash_month,
                    clash_year,
                    event_date,
                    created_at
                FROM event_clash
                WHERE season_id = %s
                ORDER BY
                    clash_year ASC,
                    clash_month ASC
                """,
                (
                    season_id,
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
                    season_id,
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
    season_id: int,
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
                    season_id,
                    clash_month,
                    clash_year,
                    event_date
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    season_id,
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

# SEASON
# ├── get_season()
# ├── get_season_by_name()
# ├── get_active_season()
# ├── get_all_seasons()
# ├── add_season()
# └── edit_season()

# CLASH
# ├── get_clash()
# ├── get_clash_by_month()
# ├── get_season_clashes()
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
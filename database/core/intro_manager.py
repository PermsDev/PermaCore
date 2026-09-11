from database.database import (
    get_core_pool,
    get_main_pool
)


# ==================================================
# USER PROFILE
# ==================================================

async def get_user_profile(
    guild_id: int,
    user_id: int
):
    """
    Mengambil profile user dari perma_main
    beserta seluruh data game.

    PROFILE DATABASE:
        perma_main

        user_db
            user_id

        user_guild_db
            user_id
            guild_id
            joined_at

        member_db
            user_id
            nickname

    GAME DATABASE:
        perma_main

        game_db
            user_id
            game_key
            value

    MESSAGE DATABASE:
        permacore

        intro_message_db
            guild_id
            user_id
            game_key
            message_id
            channel_id
    """

    # ==================================================
    # PROFILE → PERMA_MAIN
    # ==================================================

    main_pool = get_main_pool()

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

            # ==========================================
            # GAME DATA → PERMA_MAIN
            # ==========================================

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

            for game in game_rows:

                profile["games"][game[0]] = {
                    "value": game[1],
                    "message_id": None,
                    "channel_id": None
                }

    # ==================================================
    # MESSAGE DATA → PERMACORE
    # ==================================================

    core_pool = get_core_pool()

    async with core_pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    game_key,
                    message_id,
                    channel_id
                FROM intro_message_db
                WHERE guild_id = %s
                AND user_id = %s
            """, (
                guild_id,
                user_id
            ))

            message_rows = await cursor.fetchall()

            for message in message_rows:

                game_key = message[0]

                # Jika game belum ada di game_db,
                # tetap buat entry agar struktur lama
                # get_user_profile() tetap kompatibel.
                if game_key not in profile["games"]:
                    profile["games"][game_key] = {
                        "value": None,
                        "message_id": None,
                        "channel_id": None
                    }

                profile["games"][game_key]["message_id"] = message[1]
                profile["games"][game_key]["channel_id"] = message[2]

    return profile


# ==================================================
# SAVE USER PROFILE
# ==================================================

async def save_user_profile(
    guild_id: int,
    user_id: int,
    nickname: str,
    joined_at
):
    """
    Menyimpan profile user.

    DATABASE:
        perma_main

    user_db:
        user_id

    user_guild_db:
        user_id
        guild_id
        joined_at

    member_db:
        user_id
        nickname
    """

    if not nickname:
        raise ValueError(
            "nickname cannot be empty"
        )

    main_pool = get_main_pool()

    async with main_pool.acquire() as conn:

        try:

            async with conn.cursor() as cursor:

                # ==========================================
                # ENSURE USER EXISTS
                # ==========================================

                await cursor.execute("""
                    INSERT INTO user_db (
                        user_id
                    )
                    VALUES (%s)
                    ON DUPLICATE KEY UPDATE
                        user_id = user_id
                """, (
                    user_id,
                ))

                # ==========================================
                # SAVE USER-GUILD RELATION
                # ==========================================

                await cursor.execute("""
                    INSERT INTO user_guild_db (
                        user_id,
                        guild_id,
                        joined_at
                    )
                    VALUES (%s, %s, %s) 

                    ON DUPLICATE KEY UPDATE
                        joined_at = VALUES(joined_at)
                """, (
                    user_id,
                    guild_id,
                    joined_at
                ))

                # ==========================================
                # SAVE MEMBER PROFILE
                # ==========================================

                await cursor.execute("""
                    INSERT INTO member_db (
                        user_id,
                        nickname
                    )
                    VALUES (%s, %s) 

                    ON DUPLICATE KEY UPDATE
                        nickname = VALUES(nickname)
                """, (
                    user_id,
                    nickname
                ))

            await conn.commit()

        except Exception:

            await conn.rollback()
            raise


# ==================================================
# INTRO DATA
# ==================================================

async def get_user_intro(
    user_id: int
):
    """
    Mengambil seluruh data intro/game user.

    Nama function dipertahankan agar code lama
    yang menggunakan function ini tidak perlu diubah.

    DATABASE:
        perma_main

    game_db:
        user_id + game_key
    """

    main_pool = get_main_pool()

    async with main_pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    user_id,
                    game_key,
                    value
                FROM game_db
                WHERE user_id = %s
            """, (
                user_id,
            ))

            rows = await cursor.fetchall()

            return [
                {
                    "user_id": row[0],
                    "game_key": row[1],
                    "value": row[2]
                }
                for row in rows
            ]


# ==================================================
# SAVE INTRO
# ==================================================

async def save_intro(
    guild_id: int,
    user_id: int,
    game_key: str,
    value: str,
    message_id: int | None = None,
    channel_id: int | None = None
):
    """
    Menyimpan data game dan message intro.

    Nama function dipertahankan agar code lama
    tidak perlu diubah.

    GAME DATA:
        perma_main.game_db

    MESSAGE DATA:
        permacore.intro_message_db
    """

    # ==================================================
    # SAVE GAME DATA → PERMA_MAIN
    # ==================================================

    main_pool = get_main_pool()

    async with main_pool.acquire() as conn:

        try:

            async with conn.cursor() as cursor:

                await cursor.execute("""
                    INSERT INTO game_db (
                        user_id,
                        game_key,
                        value
                    )
                    VALUES (%s, %s, %s) 

                    ON DUPLICATE KEY UPDATE
                        value = VALUES(value)
                """, (
                    user_id,
                    game_key,
                    value
                ))

            await conn.commit()

        except Exception:

            await conn.rollback()
            raise

    # ==================================================
    # SAVE MESSAGE DATA → PERMACORE
    # ==================================================

    if (
        message_id is not None
        and channel_id is not None
    ):

        core_pool = get_core_pool()

        async with core_pool.acquire() as conn:

            try:

                async with conn.cursor() as cursor:

                    await cursor.execute("""
                        INSERT INTO intro_message_db (
                            guild_id,
                            user_id,
                            game_key,
                            message_id,
                            channel_id
                        )
                        VALUES (%s, %s, %s, %s, %s) 

                        ON DUPLICATE KEY UPDATE
                            message_id = VALUES(message_id),
                            channel_id = VALUES(channel_id)
                    """, (
                        guild_id,
                        user_id,
                        game_key,
                        message_id,
                        channel_id
                    ))

                await conn.commit()

            except Exception:

                await conn.rollback()
                raise


# ==================================================
# DELETE INTRO
# ==================================================

async def delete_intro(
    guild_id: int,
    user_id: int,
    game_key: str
):
    """
    Menghapus intro dari guild tertentu.

    Nama function dipertahankan agar code lama
    tidak perlu diubah.

    intro_message_db:
        Selalu dihapus dari guild tersebut.

    game_db:
        Dihapus hanya jika user sudah tidak memiliki
        message intro pada guild mana pun.
    """

    # ==================================================
    # DELETE MESSAGE → PERMACORE
    # ==================================================

    core_pool = get_core_pool()

    async with core_pool.acquire() as conn:

        try:

            async with conn.cursor() as cursor:

                # ==========================================
                # DELETE MESSAGE DARI GUILD
                # ==========================================

                await cursor.execute("""
                    DELETE FROM intro_message_db
                    WHERE guild_id = %s
                    AND user_id = %s
                    AND game_key = %s
                """, (
                    guild_id,
                    user_id,
                    game_key
                ))

                # ==========================================
                # CEK MESSAGE DI GUILD LAIN
                # ==========================================

                await cursor.execute("""
                    SELECT COUNT(*)
                    FROM intro_message_db
                    WHERE user_id = %s
                    AND game_key = %s
                """, (
                    user_id,
                    game_key
                ))

                row = await cursor.fetchone()

                remaining = row[0]

            await conn.commit()

        except Exception:

            await conn.rollback()
            raise

    # ==================================================
    # DELETE GAME DATA → PERMA_MAIN
    # ==================================================

    if remaining == 0:

        main_pool = get_main_pool()

        async with main_pool.acquire() as conn:

            try:

                async with conn.cursor() as cursor:

                    await cursor.execute("""
                        DELETE FROM game_db
                        WHERE user_id = %s
                        AND game_key = %s
                    """, (
                        user_id,
                        game_key
                    ))

                await conn.commit()

            except Exception:

                await conn.rollback()
                raise


# ==================================================
# BULK LOAD
# ==================================================

async def get_all_intro():
    """
    Mengambil seluruh data game.

    Nama function dipertahankan agar code lama
    tidak perlu diubah.

    DATABASE:
        perma_main.game_db
    """

    main_pool = get_main_pool()

    async with main_pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    user_id,
                    game_key,
                    value
                FROM game_db
            """)

            rows = await cursor.fetchall()

            return [
                {
                    "user_id": row[0],
                    "game_key": row[1],
                    "value": row[2]
                }
                for row in rows
            ]


# ==================================================
# COPYVIEW INTROS
# ==================================================

async def get_copyview_intros(
    guild_id: int
):
    """
    Mengambil message intro MLBB dan Roblox
    dari guild tertentu.

    DATABASE:
        permacore.intro_message_db
    """

    core_pool = get_core_pool()

    async with core_pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    m.user_id,
                    m.game_key,
                    m.message_id
                FROM intro_message_db AS m
                WHERE m.guild_id = %s
                AND m.game_key IN (
                    'mlbb',
                    'roblox'
                )
            """, (
                guild_id
            ))

            rows = await cursor.fetchall()

            return [
                {
                    "user_id": row[0],
                    "game_key": row[1],
                    "message_id": row[2]
                }
                for row in rows
            ]
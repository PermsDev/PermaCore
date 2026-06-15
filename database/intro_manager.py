# database/intro_manager.py

from database.database import get_connection


# ======================
# USER PROFILE
# ======================
def get_user_profile(
    guild_id: int,
    user_id: int
):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            user_id,
            guild_id,
            nickname,
            joined_at
        FROM user_db
        WHERE guild_id = %s
        AND user_id = %s
    """, (
        guild_id,
        user_id
    ))

    profile = cursor.fetchone()

    if not profile:
        cursor.close()
        conn.close()
        return {}

    cursor.execute("""
        SELECT
            game_key,
            value,
            message_id,
            channel_id
        FROM intro_db
        WHERE guild_id = %s
        AND user_id = %s
    """, (
        guild_id,
        user_id
    ))

    intros = cursor.fetchall()

    profile["games"] = {}

    for intro in intros:

        profile["games"][intro["game_key"]] = {
            "value": intro["value"],
            "message_id": intro["message_id"],
            "channel_id": intro["channel_id"]
        }

    cursor.close()
    conn.close()

    return profile

def save_user_profile(
    guild_id: int,
    user_id: int,
    nickname: str,
    joined_at
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO user_db (
            user_id,
            guild_id,
            nickname,
            joined_at
        )
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            nickname = VALUES(nickname),
            joined_at = VALUES(joined_at)
    """, (
        user_id,
        guild_id,
        nickname,
        joined_at
    ))

    conn.commit()

    cursor.close()
    conn.close()


# ======================
# INTRO DATA
# ======================

def get_user_intro(
    guild_id: int,
    user_id: int
):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            user_id,
            guild_id,
            game_key,
            value,
            message_id,
            channel_id
        FROM intro_db
        WHERE guild_id = %s
        AND user_id = %s
    """, (
        guild_id,
        user_id
    ))

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result


def get_game_intro(
    guild_id: int,
    user_id: int,
    game_key: str
):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM intro_db
        WHERE guild_id = %s
        AND user_id = %s
        AND game_key = %s
    """, (
        guild_id,
        user_id,
        game_key
    ))

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result


def save_intro(
    guild_id: int,
    user_id: int,
    game_key: str,
    value: str,
    message_id: int,
    channel_id: int
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO intro_db (
            user_id,
            guild_id,
            game_key,
            value,
            message_id,
            channel_id
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            value = VALUES(value),
            message_id = VALUES(message_id),
            channel_id = VALUES(channel_id)
    """, (
        user_id,
        guild_id,
        game_key,
        value,
        message_id,
        channel_id
    ))

    conn.commit()

    cursor.close()
    conn.close()


def delete_intro(
    guild_id: int,
    user_id: int,
    game_key: str
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM intro_db
        WHERE guild_id = %s
        AND user_id = %s
        AND game_key = %s
    """, (
        guild_id,
        user_id,
        game_key
    ))

    conn.commit()

    cursor.close()
    conn.close()

def delete_all_user_intro(
    guild_id: int,
    user_id: int
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM intro_db
        WHERE guild_id = %s
        AND user_id = %s
    """, (
        guild_id,
        user_id
    ))

    conn.commit()

    cursor.close()
    conn.close()

def delete_user_profile(
    guild_id: int,
    user_id: int
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM user_db
        WHERE guild_id = %s
        AND user_id = %s
    """, (
        guild_id,
        user_id
    ))

    conn.commit()

    cursor.close()
    conn.close()

# ======================
# BULK LOAD
# ======================

def get_all_intro():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM intro_db
    """)

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result

def get_copyview_intros():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            user_id,
            game_key,
            message_id
        FROM intro_db
        WHERE game_key IN (
            'mlbb',
            'roblox'
        )
    """)

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result
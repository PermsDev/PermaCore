# database/dm_message_manager.py

from database.database import get_connection

# =========================
# GET DM MESSAGE
# =========================
def get_dm_message(guild_id: int, user_id: int, dm_type: str) -> int | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT message_id
            FROM dm_message_db
            WHERE guild_id = %s
                AND user_id = %s
                AND dm_type = %s
            LIMIT 1
        """, (guild_id, user_id, dm_type))

        row = cursor.fetchone()
        return row["message_id"] if row else None

    finally:
        cursor.close()
        conn.close()


# =========================
# UPSERT DM MESSAGE
# =========================
def upsert_dm_message(guild_id: int, user_id: int, dm_type: str, message_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO dm_message_db (guild_id, user_id, dm_type, message_id)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                message_id = VALUES(message_id)
        """, (guild_id, user_id, dm_type, message_id))

        conn.commit()

    finally:
        cursor.close()
        conn.close()

# =========================
# DELETE DM MESSAGE
# =========================
def delete_dm_message(guild_id: int, user_id: int, dm_type: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM dm_message_db
            WHERE guild_id = %s
                AND user_id = %s
                AND dm_type = %s
        """, (guild_id, user_id, dm_type))

        conn.commit()

    finally:
        cursor.close()
        conn.close()


# =========================
# CHECK EXISTS
# =========================
def dm_message_exists(guild_id: int, user_id: int, dm_type: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT 1
            FROM dm_message_db
            WHERE guild_id = %s
                AND user_id = %s
                AND dm_type = %s
            LIMIT 1
        """, (guild_id, user_id, dm_type))

        return cursor.fetchone() is not None

    finally:
        cursor.close()
        conn.close()

# ========================
# GET ALL DM MESSAGES FOR GUILD (for checker)
# ========================
def get_all_dm_messages(guild_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT guild_id, user_id, dm_type, message_id
        FROM dm_message_db
        WHERE guild_id = %s
    """, (guild_id,))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows
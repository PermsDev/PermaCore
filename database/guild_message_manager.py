# database/guild_message_manager.py

from database.database import get_connection

# =========================
# GET MESSAGE
# =========================
def get_guild_message(guild_id: int, user_id: int, message_type: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT message_id, channel_id
            FROM guild_message_db
            WHERE guild_id = %s
                AND user_id = %s
                AND message_type = %s
            LIMIT 1
        """, (guild_id, user_id, message_type))

        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()


# =========================
# UPSERT MESSAGE
# =========================
def upsert_guild_message(
    guild_id: int,
    user_id: int,
    message_type: str,
    channel_id: int,
    message_id: int
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO guild_message_db (
                guild_id,
                user_id,
                message_type,
                channel_id,
                message_id
            )
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                channel_id = VALUES(channel_id),
                message_id = VALUES(message_id)
        """, (
            guild_id,
            user_id,
            message_type,
            channel_id,
            message_id
        ))

        conn.commit()

    finally:
        cursor.close()
        conn.close()


# =========================
# DELETE MESSAGE TYPE
# =========================
def delete_guild_message(guild_id: int, user_id: int, message_type: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM guild_message_db
            WHERE guild_id = %s
                AND user_id = %s
                AND message_type = %s
        """, (guild_id, user_id, message_type))

        conn.commit()

    finally:
        cursor.close()
        conn.close()
        
# ========================
# GET ALL MESSAGES FOR GUILD
# ========================
def get_all_guild_messages(guild_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT message_id, channel_id, user_id, message_type
        FROM guild_message_db
        WHERE guild_id = %s
    """, (guild_id,))

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result
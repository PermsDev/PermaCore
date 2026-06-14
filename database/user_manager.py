from database.database import get_connection


def ensure_user_exists(guild_id: int, user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO user_db (
                user_id,
                guild_id,
                nickname,
                joined_at
            )
            VALUES (%s, %s, NULL, NULL)
            ON DUPLICATE KEY UPDATE
                user_id = user_id
        """, (user_id, guild_id))

        conn.commit()

    finally:
        cursor.close()
        conn.close()
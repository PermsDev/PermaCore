from database.database import get_connection


def get_guild_ids(guild_key: str) -> list[int]:
    """
    Mengambil seluruh guild_id berdasarkan guild_key.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT guild_id
        FROM guild_key_db
        WHERE guild_key = %s
    """, (guild_key,))

    guild_ids = [
        row[0]
        for row in cursor.fetchall()
    ]

    cursor.close()
    conn.close()

    return guild_ids
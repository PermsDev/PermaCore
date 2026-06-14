from database.database import get_connection

# membaca semua channel untuk guild tertentu
def get_channels(guild_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT channel_key, channel_id, panel_message
        FROM channel_db
        WHERE guild_id = %s
    """, (guild_id,))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        row["channel_key"]: {
            "channel_id": row["channel_id"],
            "panel_message": row["panel_message"]
        }
        for row in rows
    }

# membaca channel tertentu berdasarkan channel_key
def get_channel(guild_id: int, channel_key: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT channel_id, panel_message
        FROM channel_db
        WHERE guild_id = %s
        AND channel_key = %s
    """, (guild_id, channel_key))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return row

# menambahkan atau memperbarui channel untuk guild tertentu
def set_channel(
    guild_id: int,
    channel_key: str,
    channel_id: int,
    panel_message: int = None
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO channel_db (
            guild_id,
            channel_key,
            channel_id,
            panel_message
        )
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            channel_id = VALUES(channel_id),
            panel_message = VALUES(panel_message)
    """, (
        guild_id,
        channel_key,
        channel_id,
        panel_message
    ))

    conn.commit()

    cursor.close()
    conn.close()

# menghapus channel untuk guild tertentu berdasarkan channel_key
def delete_channel(
    guild_id: int,
    channel_key: str
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM channel_db
        WHERE guild_id = %s
        AND channel_key = %s
    """, (
        guild_id,
        channel_key
    ))

    conn.commit()

    cursor.close()
    conn.close()

# mendapatkan semua channel game untuk guild tertentu
def get_game_channels(guild_id: int):
    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT channel_key, channel_id
        FROM channel_db
        WHERE guild_id = %s
        AND channel_key IN (
            'growtopia',
            'pw',
            'mlbb',
            'roblox'
        )
    """, (guild_id,))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        row["channel_key"]: row["channel_id"]
        for row in rows
    }
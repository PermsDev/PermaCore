from database.database import get_connection

def add_guild(guild_id: int, nama_guild: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO guild_db (guild_id, nama_guild)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE
            nama_guild = VALUES(nama_guild)
    """, (guild_id, nama_guild))

    conn.commit()

    cursor.close()
    conn.close()
    
    
def remove_guild(guild_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM guild_db WHERE guild_id = %s",
        (guild_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()
from database.database import get_connection

# =========================
# CACHE EMOJI
# =========================
EMOJIS = {}

# =========================
# LOAD SEMUA EMOJI
# =========================
def load_emojis():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT emoji_key, emoji_id
        FROM emoji_db
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    EMOJIS.clear()

    for row in rows:
        EMOJIS[row["emoji_key"]] = row["emoji_id"]

# =========================
# RELOAD CACHE
# =========================
def reload_emojis():
    load_emojis()

# =========================
# GET SEMUA EMOJI
# =========================
def get_emojis():
    return EMOJIS.copy()

# =========================
# GET EMOJI ID
# =========================
def get_emoji_id(
    emoji_key: str
):
    return EMOJIS.get(
        emoji_key
    )

# =========================
# GET FORMAT EMOJI DISCORD
# =========================
def get_emoji(
    emoji_key: str,
    default: str = "🎯"
):
    emoji_id = EMOJIS.get(
        emoji_key
    )

    if not emoji_id:
        return default

    return (
        f"<:{emoji_key}:"
        f"{emoji_id}>"
    )

# =========================
# TAMBAH / UPDATE EMOJI
# =========================
def set_emoji(
    emoji_key: str,
    emoji_id: int
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO emoji_db (
            emoji_key,
            emoji_id
        )
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE
            emoji_id = VALUES(emoji_id)
    """, (
        emoji_key,
        emoji_id
    ))

    conn.commit()

    cursor.close()
    conn.close()

    EMOJIS[emoji_key] = emoji_id

# =========================
# HAPUS EMOJI
# =========================
def delete_emoji(
    emoji_key: str
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM emoji_db
        WHERE emoji_key = %s
    """, (
        emoji_key,
    ))

    conn.commit()

    cursor.close()
    conn.close()

    EMOJIS.pop(
        emoji_key,
        None
    )
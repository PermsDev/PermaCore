from database.database import get_connection

# =========================
# CREATE / UPDATE QUEUE
# =========================
def upsert_delete_queue(
    channel_id: int,
    message_id: int,
    delete_at: float
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO delete_queue_db (
            channel_id,
            message_id,
            delete_at
        )
        VALUES (%s, %s, %s)

        ON DUPLICATE KEY UPDATE
            channel_id = VALUES(channel_id),
            delete_at = VALUES(delete_at)
    """, (
        channel_id,
        message_id,
        delete_at
    ))

    conn.commit()

    cursor.close()
    conn.close()


# =========================
# GET ALL QUEUE
# =========================
def get_delete_queue():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM delete_queue_db
        ORDER BY delete_at ASC
    """)

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result


# =========================
# GET EXPIRED QUEUE
# =========================
def get_expired_delete_queue(
    current_time: float
):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM delete_queue_db
        WHERE delete_at <= %s
        ORDER BY delete_at ASC
    """, (
        current_time,
    ))

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result


# =========================
# DELETE QUEUE ITEM
# =========================
def delete_queue_item(
    message_id: int
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM delete_queue_db
        WHERE message_id = %s
    """, (
        message_id,
    ))

    conn.commit()

    cursor.close()
    conn.close()


# =========================
# CLEAR ALL QUEUE
# =========================
def clear_delete_queue():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM delete_queue_db
    """)

    conn.commit()

    cursor.close()
    conn.close()
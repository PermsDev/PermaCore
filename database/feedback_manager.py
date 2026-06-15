# database/feedback_manager.py

from database.database import get_connection

# Function to create a new feedback entry
def create_feedback(
    message_id,
    guild_id,
    channel_id,
    category,
    user_id,
    username,
    feedback,
    sent_at
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO feedback_db (
            message_id,
            guild_id,
            channel_id,
            category,
            user_id,
            username,
            feedback,
            sent_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        message_id,
        guild_id,
        channel_id,
        category,
        user_id,
        username,
        feedback,
        sent_at
    ))

    conn.commit()
    conn.close()
    
# Function to update feedback with admin reply
def reply_feedback(
    message_id,
    admin_id,
    admin_name,
    reply,
    replied_at
):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE feedback_db
        SET
            admin_id = %s,
            admin_name = %s,
            reply = %s,
            replied_at = %s
        WHERE message_id = %s
    """, (
        admin_id,
        admin_name,
        reply,
        replied_at,
        message_id
    ))

    conn.commit()
    conn.close()

# Function to retrieve feedback by message_id
def get_feedback(message_id):
    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM feedback_db
        WHERE message_id = %s
    """, (message_id,))

    result = cursor.fetchone()

    conn.close()

    return result

# Function to retrieve all feedbacks for a guild
def get_guild_feedbacks(guild_id):
    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM feedback_db
        WHERE guild_id = %s
        ORDER BY sent_at DESC
    """, (guild_id,))

    result = cursor.fetchall()

    conn.close()

    return result

# Function to delete feedback by message_id
def delete_feedback(message_id):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM feedback_db
        WHERE message_id = %s
    """, (message_id,))

    conn.commit()
    conn.close()
    
def get_pending_feedbacks():
    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT message_id
        FROM feedback_db
        WHERE reply IS NULL
    """)

    result = cursor.fetchall()

    conn.close()

    return result
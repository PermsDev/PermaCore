# services/check/cleanup/message_db_cleanup.py
import asyncio

from database.dm_message_manager import delete_dm_message
from database.delete_queue_manager import delete_queue_item
from database.feedback_manager import delete_feedback
from database.guild_message_manager import delete_guild_message
from database.intro_manager import delete_intro


async def cleanup_message_db(missing: dict):
    """
    missing = hasil dari check_message_db()
    """

    total_deleted = 0

    # =========================
    # DM MESSAGE DB
    # =========================
    for msg_id in missing.get("dm_message_db", []):
        try:
            delete_dm_message(msg_id)
            total_deleted += 1
        except:
            pass

        await asyncio.sleep(0)

    # =========================
    # DELETE QUEUE DB
    # =========================
    for msg_id in missing.get("delete_queue_db", []):
        try:
            delete_queue_item(msg_id)
            total_deleted += 1
        except:
            pass

        await asyncio.sleep(0)

    # =========================
    # FEEDBACK DB
    # =========================
    for msg_id in missing.get("feedback_db", []):
        try:
            delete_feedback(msg_id)
            total_deleted += 1
        except:
            pass

        await asyncio.sleep(0)

    # =========================
    # GUILD MESSAGE DB
    # =========================
    for msg_id in missing.get("guild_message_db", []):
        try:
            delete_guild_message(msg_id)
            total_deleted += 1
        except:
            pass

        await asyncio.sleep(0)

    # =========================
    # INTRO DB
    # =========================
    for msg_id in missing.get("intro_db", []):
        try:
            delete_intro(msg_id)
            total_deleted += 1
        except:
            pass

        await asyncio.sleep(0)

    return total_deleted
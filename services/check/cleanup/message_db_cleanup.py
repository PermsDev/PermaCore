# services/check/cleanup/message_db_cleanup.py

import asyncio

from database.dm_message_manager import delete_dm_message
from database.delete_queue_manager import delete_queue_item
from database.feedback_manager import delete_feedback
from database.guild_message_manager import delete_guild_message
from database.intro_manager import delete_intro
from database.channel_manager import delete_channel


async def cleanup_message_db(missing: dict):
    """
    SAFE CLEANUP SYSTEM

    missing = hasil dari check_message_db()
    """

    total_deleted = 0

    print("\n" + "=" * 60)
    print("[CLEANUP] STARTING DATABASE CLEANUP")
    print("=" * 60)

    # =========================
    # DM MESSAGE DB
    # =========================
    for msg_id in missing.get("dm_message_db", []):
        try:
            print(f"[CLEANUP][DM] deleting message_id={msg_id}")
            await delete_dm_message(msg_id)
            total_deleted += 1
        except Exception as e:
            print(f"[CLEANUP ERROR][DM] {msg_id} -> {e}")

        await asyncio.sleep(0)

    # =========================
    # DELETE QUEUE DB
    # =========================
    for msg_id in missing.get("delete_queue_db", []):
        try:
            print(f"[CLEANUP][QUEUE] deleting message_id={msg_id}")
            await delete_queue_item(msg_id)
            total_deleted += 1
        except Exception as e:
            print(f"[CLEANUP ERROR][QUEUE] {msg_id} -> {e}")

        await asyncio.sleep(0)

    # =========================
    # FEEDBACK DB
    # =========================
    for msg_id in missing.get("feedback_db", []):
        try:
            print(f"[CLEANUP][FEEDBACK] deleting message_id={msg_id}")
            await delete_feedback(msg_id)
            total_deleted += 1
        except Exception as e:
            print(f"[CLEANUP ERROR][FEEDBACK] {msg_id} -> {e}")

        await asyncio.sleep(0)

    # =========================
    # GUILD MESSAGE DB
    # =========================
    for msg_id in missing.get("guild_message_db", []):
        try:
            print(f"[CLEANUP][GUILD_MSG] deleting message_id={msg_id}")
            await delete_guild_message(msg_id)
            total_deleted += 1
        except Exception as e:
            print(f"[CLEANUP ERROR][GUILD_MSG] {msg_id} -> {e}")

        await asyncio.sleep(0)

    # =========================
    # INTRO DB
    # =========================
    for msg_id in missing.get("intro_db", []):
        try:
            print(f"[CLEANUP][INTRO] deleting message_id={msg_id}")
            await delete_intro(msg_id)
            total_deleted += 1
        except Exception as e:
            print(f"[CLEANUP ERROR][INTRO] {msg_id} -> {e}")

        await asyncio.sleep(0)

    # =========================
    # CHANNEL DB (IMPORTANT)
    # =========================
    for item in missing.get("channel_db", []):
        try:
            key = item.get("key")
            channel_id = item.get("channel_id")

            print(f"[CLEANUP][CHANNEL_DB] key={key} channel_id={channel_id}")

            # delete berdasarkan guild + key
            await delete_channel(item["guild_id"], key)

            total_deleted += 1

        except Exception as e:
            print(f"[CLEANUP ERROR][CHANNEL_DB] {item} -> {e}")

        await asyncio.sleep(0)

    # =========================
    # SUMMARY
    # =========================
    print("\n" + "=" * 60)
    print(f"[CLEANUP FINISHED] TOTAL DELETED = {total_deleted}")
    print("=" * 60)

    return total_deleted
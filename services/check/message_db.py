import asyncio
import discord

from database.dm_message_manager import get_all_dm_messages
from database.delete_queue_manager import get_delete_queue
from database.feedback_manager import get_guild_feedbacks
from database.guild_message_manager import get_all_guild_messages
from database.intro_manager import get_all_intro


async def check_message_db(bot: discord.Client, guild: discord.Guild, messages: str | None = None):

    missing = {
        "dm_message_db": [],
        "delete_queue_db": [],
        "feedback_db": [],
        "guild_message_db": [],
        "intro_db": []
    }

    enabled = {
        "dm_message_db": True,
        "delete_queue_db": True,
        "feedback_db": True,
        "guild_message_db": True,
        "intro_db": True
    }

    if messages:
        for k in enabled:
            enabled[k] = (k == messages)

    async def check_message(channel_id: int, message_id: int):
        try:
            channel = bot.get_channel(channel_id)
            if not channel:
                return False

            await channel.fetch_message(message_id)
            return True

        except discord.NotFound:
            return False
        except discord.Forbidden:
            return False
        except Exception:
            return True

    # =========================
    # DM MESSAGE DB
    # =========================
    if enabled["dm_message_db"]:
        dm_rows = get_all_dm_messages(guild.id)

        dm_map = {}
        for row in dm_rows:
            dm_map[(row["user_id"], row["dm_type"])] = row["message_id"]

        for member in guild.members:
            for dm_type in ["executive", "welcome", "intro"]:

                msg_id = dm_map.get((member.id, dm_type))
                if not msg_id:
                    continue

                try:
                    dm = await member.create_dm()
                except:
                    continue

                exists = await check_message(dm.id, msg_id)

                if not exists:
                    missing["dm_message_db"].append(msg_id)

            await asyncio.sleep(0)

    # =========================
    # DELETE QUEUE DB
    # =========================
    if enabled["delete_queue_db"]:
        for item in get_delete_queue():
            exists = await check_message(item["channel_id"], item["message_id"])
            if not exists:
                missing["delete_queue_db"].append(item["message_id"])
            await asyncio.sleep(0)

    # =========================
    # FEEDBACK DB
    # =========================
    if enabled["feedback_db"]:
        for fb in get_guild_feedbacks(guild.id):
            exists = await check_message(fb["channel_id"], fb["message_id"])
            if not exists:
                missing["feedback_db"].append(fb["message_id"])
            await asyncio.sleep(0)

    # =========================
    # GUILD MESSAGE DB
    # =========================
    if enabled["guild_message_db"]:
        for msg in get_all_guild_messages(guild.id):
            exists = await check_message(msg["channel_id"], msg["message_id"])
            if not exists:
                missing["guild_message_db"].append(msg["message_id"])
            await asyncio.sleep(0)

    # =========================
    # INTRO DB
    # =========================
    if enabled["intro_db"]:
        for intro in get_all_intro():
            exists = await check_message(intro["channel_id"], intro["message_id"])
            if not exists:
                missing["intro_db"].append(intro["message_id"])
            await asyncio.sleep(0)

    return missing
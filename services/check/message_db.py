import asyncio
import discord

from database.dm_message_manager import get_all_dm_messages
from database.delete_queue_manager import get_delete_queue
from database.feedback_manager import get_guild_feedbacks
from database.guild_message_manager import get_all_guild_messages
from database.intro_manager import get_all_intro
from database.channel_manager import get_channels


async def check_message_db(
    bot: discord.Client,
    guild: discord.Guild,
    messages: str | None = None
):

    print("\n" + "=" * 60)
    print("[Check] START message_db scan")
    print("[Check] Mode:", messages or "ALL")

    missing = {
        "dm_message_db": [],
        "delete_queue_db": [],
        "feedback_db": [],
        "guild_message_db": [],
        "intro_db": [],
        "channel_db": []
    }

    enabled = {
        "dm_message_db": True,
        "delete_queue_db": True,
        "feedback_db": True,
        "guild_message_db": True,
        "intro_db": True,
        "channel_db": True
    }

    if messages:
        for k in enabled:
            enabled[k] = (k == messages)

    print("[Check] Enabled DB:", enabled)

    async def check_message(channel_id: int, message_id: int):
        print(f"   [Discord CHECK] channel={channel_id} message={message_id}")

        try:
            channel = bot.get_channel(channel_id)

            if not channel:
                print("      ↳ ❌ channel not found in cache")
                return False

            await channel.fetch_message(message_id)

            print("      ↳ ✅ exists in Discord")
            return True

        except discord.NotFound:
            print("      ↳ ❌ NOT FOUND (deleted)")
            return False

        except discord.Forbidden:
            print("      ↳ ❌ FORBIDDEN")
            return False

        except Exception as e:
            print(f"      ↳ ⚠️ ERROR: {e}")
            return True

    # =========================
    # DM MESSAGE DB
    # =========================
    if enabled["dm_message_db"]:
        print("\n[DM] Loading database...")

        dm_rows = await get_all_dm_messages(guild.id)

        print(f"[DM] Total rows: {len(dm_rows)}")

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

                print(f"[DM] Checking user={member.id} type={dm_type}")

                exists = await check_message(dm.id, msg_id)

                if not exists:
                    print(f"   ↳ ❌ MISSING DM message {msg_id}")
                    missing["dm_message_db"].append(msg_id)

            await asyncio.sleep(0)

    # =========================
    # DELETE QUEUE DB
    # =========================
    if enabled["delete_queue_db"]:
        print("\n[DELETE QUEUE] Loading...")

        queue = await get_delete_queue()
        print(f"[DELETE QUEUE] Total: {len(queue)}")

        for item in queue:

            print(f"[DELETE] Checking msg={item['message_id']}")

            exists = await check_message(item["channel_id"], item["message_id"])

            if not exists:
                print("   ↳ ❌ MISSING")
                missing["delete_queue_db"].append(item["message_id"])

            await asyncio.sleep(0)

    # =========================
    # FEEDBACK DB
    # =========================
    if enabled["feedback_db"]:
        print("\n[FEEDBACK] Loading...")

        feedbacks = await get_guild_feedbacks(guild.id)
        print(f"[FEEDBACK] Total: {len(feedbacks)}")

        for fb in feedbacks:

            print(f"[FEEDBACK] msg={fb['message_id']}")

            exists = await check_message(fb["channel_id"], fb["message_id"])

            if not exists:
                print("   ↳ ❌ MISSING")
                missing["feedback_db"].append(fb["message_id"])

            await asyncio.sleep(0)
            
    # =========================
    # CHANNEL DB (PANEL CHECK)
    # =========================
    if enabled["channel_db"]:
        print("\n[CHANNEL DB] Loading...")

        channels = await get_channels(guild.id)
        print(f"[CHANNEL DB] Total channels: {len(channels)}")

        missing["channel_db"] = []

        for key, data in channels.items():

            channel_id = data["channel_id"]
            panel_msg = data.get("panel_message")

            print(f"\n[CHANNEL DB] key={key}")
            print(f"   ↳ channel_id={channel_id}")
            print(f"   ↳ panel_message={panel_msg}")

            # =========================
            # CHECK CHANNEL EXIST
            # =========================
            channel = bot.get_channel(channel_id)

            if not channel:
                print("   ↳ ❌ CHANNEL NOT FOUND IN DISCORD")
                missing["channel_db"].append({
                    "key": key,
                    "channel_id": channel_id,
                    "reason": "CHANNEL_NOT_FOUND"
                })
                continue

            print(f"   ↳ ✅ Channel found: #{channel.name}")

            # =========================
            # CHECK PANEL MESSAGE
            # =========================
            if panel_msg:

                try:
                    msg = await channel.fetch_message(panel_msg)
                    print(f"   ↳ ✅ Panel message exists: {msg.id}")

                except discord.NotFound:
                    print("   ↳ ❌ PANEL MESSAGE NOT FOUND (deleted)")
                    missing["channel_db"].append({
                        "key": key,
                        "channel_id": channel_id,
                        "panel_message": panel_msg,
                        "reason": "PANEL_MESSAGE_NOT_FOUND"
                    })

                except discord.Forbidden:
                    print("   ↳ ❌ NO PERMISSION TO FETCH MESSAGE")

                    missing["channel_db"].append({
                        "key": key,
                        "channel_id": channel_id,
                        "panel_message": panel_msg,
                        "reason": "FORBIDDEN"
                    })

            else:
                print("   ↳ ⚠️ No panel message set")

        # =========================
        # GUILD MESSAGE DB
        # =========================
        if enabled["guild_message_db"]:
            print("\n[GUILD MSG] Loading...")

            msgs = await get_all_guild_messages(guild.id)
            print(f"[GUILD MSG] Total: {len(msgs)}")

            for msg in msgs:

                print(f"[GUILD MSG] msg={msg['message_id']}")

                exists = await check_message(msg["channel_id"], msg["message_id"])

                if not exists:
                    print("   ↳ ❌ MISSING")
                    missing["guild_message_db"].append(msg["message_id"])

                await asyncio.sleep(0)

    # =========================
    # INTRO DB
    # =========================
    if enabled["intro_db"]:
        print("\n[INTRO] Loading...")

        intros = await get_all_intro()
        print(f"[INTRO] Total: {len(intros)}")

        for intro in intros:

            print(f"[INTRO] msg={intro['message_id']}")

            exists = await check_message(intro["channel_id"], intro["message_id"])

            if not exists:
                print("   ↳ ❌ MISSING")
                missing["intro_db"].append(intro["message_id"])

            await asyncio.sleep(0)

    print("\n" + "=" * 60)
    print("[Check FINISHED] Summary:")
    for k, v in missing.items():
        print(f" - {k}: {len(v)} missing")

    return missing
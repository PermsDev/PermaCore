import discord

from utils.logger import send_log
from database.user_manager import ensure_user_exists
from database.dm_message_manager import (
    upsert_dm_message,
    delete_dm_message
)


async def handle_member_join(member: discord.Member):

    guild = member.guild
    guild_id = guild.id
    user_id = member.id

    print(f"{member} joined {guild.name}")

    # ======================
    # ENSURE USER EXISTS (WAJIB UNTUK FK)
    # ======================
    await ensure_user_exists(guild_id, user_id)

    # ======================
    # GET DM CHANNEL
    # ======================
    try:
        dm_channel = member.dm_channel or await member.create_dm()

        # ======================
        # CLEAN OLD BOT MESSAGES ONLY
        # ======================
        async for message in dm_channel.history(limit=50):

            # ✔ FIX: pakai bot flag (bukan member.bot.id)
            if not message.author.bot:
                continue

            try:
                await message.delete()

            except discord.Forbidden:
                print(f"[FORBIDDEN DM DELETE] {member}")
                break

            except discord.NotFound:
                continue

            except Exception as e:
                print(f"[ERROR DELETE DM] {e}")

    except Exception as e:
        print(f"[DM CLEAN FAILED] {e}")

    # ======================
    # SEND NEW WELCOME MESSAGE
    # ======================
    try:

        welcome_message = await member.send(

            f"## Selamat datang di server {member.guild.name}! <a:hi_man:1478080922883719238>\n"
            
            "Untuk Melanjutkan Progres Masuk Server, silahkan melakukan introduction dengan mengikuti langkah-langkah berikut:\n\n"
            
            "### <a:statusOffline:1478032435164741777> Role 1: Verified Introduction (2)\n"
            "- Kunjungi Channel <#1501234394076020806>\n"
            "- Isi formulir introduction untuk mendapatkan role Verified Introduction 2\n"
        )

        # ======================
        # SAVE DM PER GUILD (IMPORTANT FIX)
        # ======================

        # ✔ hapus DM hanya untuk guild ini + user ini + type joined
        await delete_dm_message(guild_id, user_id, "joined")

        # ✔ simpan DM baru untuk guild ini saja
        await upsert_dm_message(
            guild_id,
            user_id,
            "joined",
            welcome_message.id
        )

        await send_log(
            guild=guild,
            log_type="INFORMATION",
            action="Member Join",
            emoji="👋",
            user=member
        )

    except discord.Forbidden:
        print(f"[DM BLOCKED] {member}")

    except Exception as e:
        print(f"[WELCOME DM ERROR] {e}")

    # ======================
    # PUBLIC WELCOME
    # ======================
    channel = discord.utils.get(guild.text_channels, name="general")

    if channel:
        await channel.send(f"👋 Welcome {member.mention}!")
from database.intro_manager import (
    get_user_profile
)

from database.guild_message_manager import (
    get_guild_message
)

import discord
from utils.logger import send_log


async def handle_member_main_remove(member):

    print(f"{member} keluar...")

    # ==================================================
    # LOAD INTRO DATA
    # ==================================================
    intro_data = await get_user_profile(member.guild.id, member.id) or {}

    games = intro_data.get("games", {})

    # ==================================================
    # HAPUS INTRO MESSAGES (DISCORD)
    # ==================================================
    for game_name, game_data in games.items():

        channel_id = game_data.get("channel_id")
        message_id = game_data.get("message_id")

        if not channel_id or not message_id:
            continue

        channel = member.guild.get_channel(int(channel_id))

        if not channel:
            print(f"Channel {channel_id} tidak ditemukan.")
            continue

        try:
            message = await channel.fetch_message(int(message_id))
            await message.delete()

            print(f"Message {game_name} untuk {member} berhasil dihapus.")

        except discord.NotFound:
            print(f"Message {game_name} tidak ditemukan.")

        except discord.Forbidden:
            print(f"Tidak ada izin hapus message {game_name}.")

        except discord.HTTPException as e:
            print(f"Gagal hapus {game_name}: {e}")

    # ==================================================
    # HAPUS WELCOME MESSAGE (DISCORD)
    # ==================================================
    welcome_data = await get_guild_message(
        member.guild.id,
        member.id,
        "welcome"
    )

    if welcome_data:

        channel_id = welcome_data.get("channel_id")
        message_id = welcome_data.get("message_id")

        channel = member.guild.get_channel(int(channel_id)) if channel_id else None

        if channel and message_id:

            try:
                message = await channel.fetch_message(int(message_id))
                await message.delete()

                print(f"Welcome message {member} berhasil dihapus.")

            except discord.NotFound:
                print("Welcome message tidak ditemukan.")

            except discord.Forbidden:
                print("Tidak ada izin hapus welcome message.")

            except discord.HTTPException as e:
                print(f"Gagal hapus welcome message: {e}")

        else:
            print(f"Channel welcome {channel_id} tidak ditemukan.")

    # ==================================================
    # LOGGING
    # ==================================================
    await send_log(
        guild=member.guild,
        log_type="INFORMATION",
        action="Member Remove",
        emoji="<a:statusOffline:1478032435164741777>",
        user=member
    )
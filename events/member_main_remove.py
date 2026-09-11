import discord

from database.core.intro_manager import (
    get_user_profile
)

from database.core.guild_message_manager import (
    get_guild_message
)

from database.core.emoji_manager import get_emoji

from utils.logger import send_log


async def handle_member_main_remove(member):

    print(f"{member} keluar...")

    guild_id = member.guild.id
    user_id = member.id

    # ==================================================
    # LOAD USER PROFILE
    # ==================================================

    profile = await get_user_profile(
        guild_id=guild_id,
        user_id=user_id
    )

    # ==================================================
    # HAPUS INTRO MESSAGES (DISCORD)
    # ==================================================

    games = profile.get("games", {})

    for game_key, game_data in games.items():

        channel_id = game_data.get("channel_id")
        message_id = game_data.get("message_id")

        if not channel_id or not message_id:
            continue

        channel = member.guild.get_channel(
            int(channel_id)
        )

        if not channel:
            print(
                f"Channel {channel_id} "
                f"untuk {game_key} tidak ditemukan."
            )
            continue

        try:
            message = await channel.fetch_message(
                int(message_id)
            )

            await message.delete()

            print(
                f"Message {game_key} untuk "
                f"{member} berhasil dihapus."
            )

        except discord.NotFound:
            print(
                f"Message {game_key} "
                f"tidak ditemukan."
            )

        except discord.Forbidden:
            print(
                f"Tidak ada izin hapus "
                f"message {game_key}."
            )

        except discord.HTTPException as e:
            print(
                f"Gagal hapus {game_key}: {e}"
            )

    # ==================================================
    # HAPUS WELCOME MESSAGE (DISCORD)
    # ==================================================

    welcome_data = await get_guild_message(
        guild_id,
        user_id,
        "welcome"
    )

    if welcome_data:

        channel_id = welcome_data.get("channel_id")
        message_id = welcome_data.get("message_id")

        channel = (
            member.guild.get_channel(int(channel_id))
            if channel_id
            else None
        )

        if channel and message_id:

            try:
                message = await channel.fetch_message(
                    int(message_id)
                )

                await message.delete()

                print(
                    f"Welcome message {member} "
                    f"berhasil dihapus."
                )

            except discord.NotFound:
                print(
                    "Welcome message "
                    "tidak ditemukan."
                )

            except discord.Forbidden:
                print(
                    "Tidak ada izin hapus "
                    "welcome message."
                )

            except discord.HTTPException as e:
                print(
                    f"Gagal hapus welcome message: {e}"
                )

        else:
            print(
                f"Channel welcome {channel_id} "
                f"tidak ditemukan."
            )

    # ==================================================
    # LOGGING
    # ==================================================

    await send_log(
        guild=member.guild,
        log_type="INFORMATION",
        action="Member Remove",
        emoji=get_emoji("statusOffline"),
        user=member
    )

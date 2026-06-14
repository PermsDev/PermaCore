from database.intro_manager import (
    get_user_profile,
    delete_all_user_intro,
    delete_user_profile
)

from database.guild_message_manager import (
    get_guild_message,
    delete_guild_message
)

import discord

from utils.logger import send_log


async def handle_member_remove(member):

    print(f"{member} keluar...")

    # ======================
    # LOAD DATA
    # ======================
    intro_data = get_user_profile(
        member.guild.id,
        member.id
    )

    # ==================================================
    # HAPUS INTRO MESSAGE
    # ==================================================
    games = intro_data.get(
        "games",
        {}
    )

    for game_name, game_data in games.items():

        channel_id = game_data.get(
            "channel_id"
        )

        message_id = game_data.get(
            "message_id"
        )

        if not channel_id or not message_id:
            continue

        channel = member.guild.get_channel(
            int(channel_id)
        )

        if not channel:

            print(
                f"Channel {channel_id} "
                f"tidak ditemukan."
            )

            continue

        try:

            message = await channel.fetch_message(
                int(message_id)
            )

            await message.delete()

            print(
                f"Message {game_name} "
                f"untuk {member} "
                f"berhasil dihapus."
            )

        except discord.NotFound:

            print(
                f"Message {game_name} "
                f"tidak ditemukan."
            )

        except discord.Forbidden:

            print(
                f"Tidak ada izin hapus "
                f"message {game_name}."
            )

        except discord.HTTPException as e:

            print(
                f"Gagal hapus "
                f"{game_name}: {e}"
            )

    # ==================================================
    # HAPUS DATA INTRO DATABASE
    # ==================================================
    delete_all_user_intro(
        member.guild.id,
        member.id
    )

    delete_user_profile(
        member.guild.id,
        member.id
    )

    print(
        f"Data intro {member} "
        f"berhasil dihapus."
    )

    # ==================================================
    # HAPUS WELCOME MESSAGE (DATABASE)
    # ==================================================
    welcome_data = get_guild_message(
        member.guild.id,
        member.id,
        "welcome"
    )

    if welcome_data:

        channel_id = welcome_data["channel_id"]
        message_id = welcome_data["message_id"]

        channel = member.guild.get_channel(
            int(channel_id)
        )

        if channel:

            try:

                message = await channel.fetch_message(
                    int(message_id)
                )

                await message.delete()

                print(
                    f"Welcome message "
                    f"{member} berhasil dihapus."
                )

            except discord.NotFound:

                print(
                    f"Welcome message "
                    f"tidak ditemukan."
                )

            except discord.Forbidden:

                print(
                    f"Tidak ada izin "
                    f"hapus welcome message."
                )

            except discord.HTTPException as e:

                print(
                    f"Gagal hapus "
                    f"welcome message: {e}"
                )

        else:

            print(
                f"Channel welcome "
                f"{channel_id} tidak ditemukan."
            )

        # ======================
        # HAPUS DATA DATABASE
        # ======================
        delete_guild_message(
            member.guild.id,
            member.id,
            "welcome"
        )

        print(
            f"Data welcome {member} "
            f"berhasil dihapus."
        )
    
    # ==================================================
    # LOGGER
    # ==================================================
    await send_log(
        guild=member.guild,
        log_type="INFORMATION",
        action="Member Remove",
        emoji="<a:statusOffline:1478032435164741777>",
        user=member
    )

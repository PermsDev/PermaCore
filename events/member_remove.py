from utils.json_manager import (
    INTRO_DATA_PATH,
    GUILD_MESSAGES_PATH,
    load_json,
    save_json
)

import discord

from utils.logger import send_log


async def handle_member_remove(member):

    print(f"{member} keluar...")

    guild_id = str(member.guild.id)
    user_id = str(member.id)

    # ======================
    # LOAD DATA
    # ======================
    data_intro = await load_json(
        INTRO_DATA_PATH
    )

    data_guild_messages = await load_json(
        GUILD_MESSAGES_PATH
    )

    # ==================================================
    # HAPUS INTRO MESSAGE
    # ==================================================
    if (
        guild_id in data_intro
        and user_id in data_intro[guild_id]
    ):

        user_data = data_intro[guild_id][user_id]

        games = user_data.get(
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
                channel_id
            )

            if not channel:

                print(
                    f"Channel {channel_id} "
                    f"tidak ditemukan."
                )

                continue

            try:

                message = await channel.fetch_message(
                    message_id
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

        # ======================
        # HAPUS DATA USER INTRO
        # ======================
        del data_intro[guild_id][user_id]

        print(
            f"Data intro {member} "
            f"berhasil dihapus."
        )

    # ==================================================
    # HAPUS WELCOME MESSAGE
    # ==================================================
    if (
        guild_id in data_guild_messages
        and user_id in data_guild_messages[guild_id]
    ):

        user_data = data_guild_messages[guild_id][user_id]

        welcome_data = user_data.get(
            "welcome",
            {}
        )

        channel_id = welcome_data.get(
            "channel_id"
        )

        message_id = welcome_data.get(
            "message_id"
        )

        if channel_id and message_id:

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
        # HAPUS DATA USER
        # ======================
        del data_guild_messages[guild_id][user_id]

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

    # ======================
    # SAVE JSON
    # ======================
    await save_json(
        INTRO_DATA_PATH,
        data_intro
    )

    await save_json(
        GUILD_MESSAGES_PATH,
        data_guild_messages
    )
    

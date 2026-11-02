import discord

from services.helper.delate_discord_message import delete_discord_message
from database.core.guild_message_manager import (
    get_guild_message,
    delete_guild_message
)

# ======================
# MEMBER REMOVE WELCOME
# ======================

async def handle_member_remove_welcome(
    member: discord.Member
):

    guild_id = member.guild.id
    user_id = member.id

    # DELETE WELCOME DISCORD MESSAGE

    try:

        welcome_data = await get_guild_message(
            guild_id,
            user_id,
            "welcome"
        )

        if welcome_data:

            channel_id = welcome_data.get("channel_id")
            message_id = welcome_data.get("message_id")

            if channel_id and message_id:

                await delete_discord_message(
                    guild=member.guild,
                    channel_id=channel_id,
                    message_id=message_id,
                    label=f"Welcome message untuk {member}"
                )

    except Exception as e:

        print(
            f"Gagal menghapus Welcome Discord {member}: {e}"
        )

    # DELETE WELCOME DATABASE

    try:

        await delete_guild_message(
            guild_id,
            user_id,
            "welcome"
        )

        print(
            f"Welcome DB {member} berhasil dihapus."
        )

    except Exception as e:

        print(
            f"Gagal menghapus Welcome DB {member}: {e}"
        )

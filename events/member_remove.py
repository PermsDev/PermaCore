import discord

from discord.ext import commands

from database.core.intro_manager import (
    get_user_profile,
    delete_user_intro_messages
)

from database.core.guild_message_manager import (
    get_guild_message,
    delete_guild_message
)

from database.core.emoji_manager import get_emoji

from utils.logger import send_log


# ======================
# DELETE DISCORD MESSAGE
# ======================

async def delete_discord_message(
    guild: discord.Guild,
    channel_id: int,
    message_id: int,
    label: str
):

    channel = guild.get_channel(
        int(channel_id)
    )

    if not channel:
        print(
            f"Channel {channel_id} untuk {label} tidak ditemukan."
        )
        return

    try:

        message = await channel.fetch_message(
            int(message_id)
        )

        await message.delete()

        print(
            f"{label} berhasil dihapus."
        )

    except discord.NotFound:

        print(
            f"{label} tidak ditemukan."
        )

    except discord.Forbidden:

        print(
            f"Tidak ada izin menghapus {label}."
        )

    except discord.HTTPException as e:

        print(
            f"Gagal menghapus {label}: {e}"
        )


# ======================
# DELETE INTRO MESSAGES
# ======================

async def delete_member_intro_messages(
    member: discord.Member
):

    profile = await get_user_profile(
        guild_id=member.guild.id,
        user_id=member.id
    ) or {}

    games = profile.get(
        "games",
        {}
    )

    for game_key, game_data in games.items():

        channel_id = game_data.get("channel_id")
        message_id = game_data.get("message_id")

        if not channel_id or not message_id:
            continue

        await delete_discord_message(
            guild=member.guild,
            channel_id=channel_id,
            message_id=message_id,
            label=f"Introduction {game_key} untuk {member}"
        )


# ======================
# DELETE WELCOME MESSAGE
# ======================

async def delete_member_welcome_message(
    member: discord.Member
):

    welcome_data = await get_guild_message(
        member.guild.id,
        member.id,
        "welcome"
    )

    if not welcome_data:
        return

    channel_id = welcome_data.get("channel_id")
    message_id = welcome_data.get("message_id")

    if not channel_id or not message_id:
        return

    await delete_discord_message(
        guild=member.guild,
        channel_id=channel_id,
        message_id=message_id,
        label=f"Welcome message untuk {member}"
    )


# ======================
# DELETE DATABASE
# ======================

async def handle_member_remove_database(
    member: discord.Member
):

    guild_id = member.guild.id
    user_id = member.id

    # DELETE INTRO MESSAGE DATABASE

    try:

        deleted = await delete_user_intro_messages(
            guild_id=guild_id,
            user_id=user_id
        )

        print(
            f"Intro DB {member}: "
            f"{deleted} record berhasil dihapus."
        )

    except Exception as e:

        print(
            f"Gagal hapus intro DB {member}: {e}"
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
            f"Gagal hapus welcome DB {member}: {e}"
        )


# ======================
# MEMBER REMOVE COG
# ======================

class MemberRemove(commands.Cog):

    def __init__(
        self,
        bot: commands.Bot
    ):

        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(
        self,
        member: discord.Member
    ):

        if member.bot:
            return

        print(
            f"[LEFT] {member} left "
            f"{member.guild.name} ({member.guild.id})"
        )

        # DELETE INTRO DISCORD MESSAGES

        try:

            await delete_member_intro_messages(
                member
            )

        except Exception as e:

            print(
                f"Gagal menghapus Introduction messages {member}: {e}"
            )

        # DELETE WELCOME DISCORD MESSAGE

        try:

            await delete_member_welcome_message(
                member
            )

        except Exception as e:

            print(
                f"Gagal menghapus Welcome message {member}: {e}"
            )

        # DELETE DATABASE RECORDS

        await handle_member_remove_database(
            member
        )

        # SEND LOG

        try:

            await send_log(
                guild=member.guild,
                log_type="INFORMATION",
                action="Member Remove",
                emoji=get_emoji("statusOffline"),
                user=member
            )

        except Exception as e:

            print(
                f"Gagal mengirim Member Remove log: {e}"
            )


# ======================
# SETUP COG
# ======================

async def setup(
    bot: commands.Bot
):

    await bot.add_cog(
        MemberRemove(bot)
    )

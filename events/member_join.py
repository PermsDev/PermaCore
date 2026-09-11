import discord

from utils.logger import send_log
from database.main.user.user_guild_manager import ensure_user_guild_exists
from database.core.emoji_manager import get_emoji
from database.core.channel_manager import get_channel
from services.bots.env_service import can_interact_with_user


async def handle_member_join(
    member: discord.Member
):
    guild = member.guild
    guild_id = guild.id
    user_id = member.id

    print(f"{member} joined {guild.name}")

    # ======================
    # ENSURE USER & GUILD
    # ======================
    await ensure_user_guild_exists(
        user_id=user_id,
        guild_id=guild_id
    )

    # ======================
    # UNVERIFIED MESSAGE
    # ======================
    if can_interact_with_user(user_id):

        channel_data = await get_channel(
            guild_id,
            "UN_VERIFIED"
        )

        if channel_data:
            channel = guild.get_channel(
                int(channel_data["channel_id"])
            )

            if channel:
                await channel.send(
                    f"Hi, {member.mention} <:hi:1473630666922004562>\n\n"
                    f"⚠️ Jika kalian membaca pesan ini menandakan kalian "
                    f"masih belum melakukan verifikasi.\n\n"
                    f"Untuk melakukan verifikasi silahkan kunjungi channel "
                    f"<#1501234394076020806> dan mengisi form introduction "
                    f"yang ada disana.\n\n"
                    f"Jika kalian mengalami Kendala dalam melakukan verifikasi, "
                    f"silahkan chat disini."
                )

    # ======================
    # LOG
    # ======================
    await send_log(
        guild=member.guild,
        log_type="INFORMATION",
        action="Member Join",
        emoji=get_emoji("statusOnline"),
        user=member
    )

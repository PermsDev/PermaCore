import discord

from database.core.channel_manager import get_channel
from services.bots.env_service import can_interact_with_user
from config.constants import UN_VERIFIED_CHANNEL_KEY


async def handle_member_join_unverified(
    member: discord.Member
):
    if not can_interact_with_user(member.id):
        return

    channel_data = await get_channel(
        member.guild.id,
        UN_VERIFIED_CHANNEL_KEY
    )

    if not channel_data:
        return

    channel = member.guild.get_channel(
        int(channel_data["channel_id"])
    )

    if not channel:
        return

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
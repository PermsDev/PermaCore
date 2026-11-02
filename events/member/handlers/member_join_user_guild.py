import discord

from database.main.user.user_guild_manager import ensure_user_guild_exists


async def handle_member_join_user_guild(
    member: discord.Member
):
    await ensure_user_guild_exists(
        user_id=member.id,
        guild_id=member.guild.id,
        joined_at=member.joined_at.replace(tzinfo=None)
        if member.joined_at
        else None
    )
    
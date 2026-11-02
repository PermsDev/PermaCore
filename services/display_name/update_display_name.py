import discord

from services.display_name.get_display_name import (
    get_display_name
)


async def update_display_name(
    member: discord.Member
) -> bool:

    nickname = await get_display_name(
        guild_id=member.guild.id,
        user_id=member.id
    )

    if not nickname:
        return False

    nickname = nickname.strip()

    if not nickname:
        return False

    try:
        await member.edit(
            nick=nickname
        )

        return True

    except discord.Forbidden:
        return False

    except discord.HTTPException:
        return False

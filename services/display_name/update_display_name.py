import discord

from database.core.role_manager import get_roles
from services.display_name.get_display_name import (
    get_display_name
)


# ======================
# UPDATE DISPLAY NAME
# ======================

async def update_display_name(
    member: discord.Member
) -> bool:
    """
    Mengubah nickname Discord member.

    Nama dasar diambil dari get_display_name().
    Jika display source user tidak tersedia,
    get_display_name() diharapkan mengembalikan nickname.

    Rules:
        - Executive Guild      -> ❄️
        - Executive SinyalID   -> 📶
    """

    # ======================
    # GET DISPLAY NAME
    # ======================

    nickname = await get_display_name(
        guild_id=member.guild.id,
        user_id=member.id
    )

    if not nickname:
        return False

    nickname = nickname.strip()

    if not nickname:
        return False

    # ======================
    # GET ROLES
    # ======================

    roles = await get_roles(
        member.guild.id
    ) or {}

    role_ids = roles.get(
        "by_key",
        {}
    )

    executive_guild_id = role_ids.get(
        "executive_guild"
    )

    executive_sinyalid_id = role_ids.get(
        "executive_sinyalid"
    )

    # ======================
    # CHECK ROLE
    # ======================

    member_role_ids = {
        role.id
        for role in member.roles
    }

    has_executive_guild = (
        executive_guild_id is not None
        and executive_guild_id in member_role_ids
    )

    has_executive_sinyalid = (
        executive_sinyalid_id is not None
        and executive_sinyalid_id in member_role_ids
    )

    # ======================
    # BUILD NICKNAME
    # ======================

    suffixes = []

    if has_executive_guild:
        suffixes.append("❄️")

    if has_executive_sinyalid:
        suffixes.append("📶")

    final_nickname = nickname

    if suffixes:
        final_nickname = (
            f"{nickname} "
            f"{' '.join(suffixes)}"
        )

    # ======================
    # UPDATE DISCORD
    # ======================

    try:

        await member.edit(
            nick=final_nickname
        )

        return True

    except discord.Forbidden:
        return False

    except discord.HTTPException:
        return False
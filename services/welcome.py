import asyncio
import json
import discord

from events.member_role_update import (
    process_welcome,
    get_role_groups
)

ROLE_GROUP_FILE = "data/role_group.json"


# =========================
# CHECK ROLE
# =========================
def has_pangkat_role(member, pangkat_roles):

    member_role_ids = {
        role.id
        for role in member.roles
    }

    return bool(
        member_role_ids & pangkat_roles
    )


# =========================
# SERVICE
# =========================
async def update_welcome_service(
    interaction: discord.Interaction,
    user: discord.Member = None
):

    guild = interaction.guild

    role_groups = await get_role_groups(
        guild.id
    )

    pangkat_roles = set(
        role_groups.get(
            "pangkat",
            {}
        ).values()
    )

    # =========================
    # SINGLE USER
    # =========================
    if user:

        # VALIDASI ROLE
        if not has_pangkat_role(
            user,
            pangkat_roles
        ):
            return (
                "❌ User tersebut tidak memiliki "
                "role pangkat yang diizinkan."
            )

        await process_welcome(user)

        return (
            f"✅ Updated welcome for "
            f"{user.mention}"
        )

    # =========================
    # ALL USERS
    # =========================
    updated = 0

    for member in guild.members:

        # skip bot
        if member.bot:
            continue

        # hanya user dengan role pangkat
        if not has_pangkat_role(
            member,
            pangkat_roles
        ):
            continue

        await process_welcome(member)

        updated += 1

        # anti rate limit
        await asyncio.sleep(0.5)

    return f"✅ Updated {updated} members."

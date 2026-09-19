import asyncio
import discord

from database.core.role_manager import get_roles
from events.member_role_update import process_welcome


# =========================
# CHECK PANGKAT
# =========================
def has_pangkat_role(
    member: discord.Member,
    role_groups: dict
) -> bool:

    member_role_ids = {role.id for role in member.roles}

    pangkat_group = (
        role_groups
        .get("by_group", {})
        .get("pangkat", {})
    )

    for role_id in pangkat_group.values():

        if role_id is None:
            continue

        if int(role_id) in member_role_ids:
            return True

    return False


# =========================
# SERVICE
# =========================
async def update_welcome_service(
    interaction: discord.Interaction,
    user: discord.Member = None
):

    guild = interaction.guild

    # =========================
    # LOAD ROLES FROM DATABASE
    # =========================
    role_groups = await get_roles(guild.id)

    # =========================
    # SINGLE USER
    # =========================
    if user:

        if user.bot:
            return "❌ Bot tidak dapat di-update."

        if not has_pangkat_role(user, role_groups):
            return (
                "❌ User tersebut tidak memiliki "
                "role group `pangkat`."
            )

        await process_welcome(user)

        return f"✅ Updated welcome for {user.mention}"

    # =========================
    # ALL USERS
    # =========================
    updated = 0

    print(
        f"[Welcome Update] Starting update for all members "
        f"in guild: {guild.name} ({guild.id})"
    )

    for member in guild.members:

        if member.bot:
            continue

        if not has_pangkat_role(member, role_groups):
            continue

        await process_welcome(member)

        updated += 1

        print(
            f"[Welcome Update] Updated: "
            f"{member} ({member.id})"
        )

        await asyncio.sleep(2)

    print(
        f"[Welcome Update] Finished. "
        f"Total updated: {updated}"
    )

    return f"✅ Updated {updated} members."
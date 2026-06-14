import asyncio
import discord

from database.role_manager import get_roles
from events.member_role_update import process_welcome


# =========================
# CHECK ROLE
# =========================
def has_pangkat_role(member, pangkat_roles: set):

    member_role_ids = {role.id for role in member.roles}

    # pastikan semua jadi int (biar aman dari DB string)
    pangkat_roles = {int(r) for r in pangkat_roles}

    # FIX: cukup return boolean intersection
    return bool(member_role_ids & pangkat_roles)


# =========================
# SERVICE
# =========================
async def update_welcome_service(
    interaction: discord.Interaction,
    user: discord.Member = None
):

    guild = interaction.guild

    # =========================
    # LOAD ROLES FROM DB
    # =========================
    role_groups = get_roles(guild.id)

    pangkat_roles = set(
        role_groups.get("pangkat", {}).values()
    )

    # safety conversion (penting karena MySQL kadang string)
    pangkat_roles = {int(r) for r in pangkat_roles if r is not None}

    # =========================
    # SINGLE USER
    # =========================
    if user:

        if not has_pangkat_role(user, pangkat_roles):
            return "❌ User tersebut tidak memiliki role pangkat yang diizinkan."

        await process_welcome(user)

        return f"✅ Updated welcome for {user.mention}"

    # =========================
    # ALL USERS
    # =========================
    updated = 0

    for member in guild.members:

        if member.bot:
            continue

        if not has_pangkat_role(member, pangkat_roles):
            continue

        await process_welcome(member)
        updated += 1

        await asyncio.sleep(0.5)

    return f"✅ Updated {updated} members."
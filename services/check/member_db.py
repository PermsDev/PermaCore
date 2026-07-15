import discord

from database.user_manager import (
    get_all_users,
    ensure_user_exists,
)


async def check_member_db(guild: discord.Guild):

    print("\n" + "=" * 60)
    print("[Check] START member_db scan")

    # =========================
    # Discord Members
    # =========================

    discord_members = {
        member.id: member
        for member in guild.members
        if not member.bot
    }

    print(f"[Discord] Members : {len(discord_members)}")

    # =========================
    # Database Users
    # =========================

    rows = await get_all_users(guild.id)

    db_users = {
        row["user_id"]
        for row in rows
    }

    print(f"[Database] Users : {len(db_users)}")

    # =========================
    # Missing in DB
    # =========================

    added = []

    for user_id, member in discord_members.items():

        if user_id in db_users:
            continue

        print(f"➕ Add user {user_id}")

        await ensure_user_exists(
            guild.id,
            user_id
        )

        added.append(user_id)

    # =========================
    # Orphan Users
    # =========================

    orphan = []

    for user_id in db_users:

        if user_id not in discord_members:

            print(f"❌ Orphan user {user_id}")

            orphan.append(user_id)

    print("=" * 60)

    return {
        "added": added,
        "orphan": orphan,
        "discord": len(discord_members),
        "database": len(db_users),
    }
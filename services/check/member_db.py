import discord

from database.user_manager import (
    get_all_users,
    ensure_users_exist,
)


async def check_member_db(
    guild: discord.Guild
):

    print("\n" + "=" * 60)
    print("[Check] START member_db scan")

    # ======================================================
    # Discord Members
    # ======================================================

    print("\n[Discord] Loading guild members...")

    discord_members = {
        member.id: member
        for member in guild.members
        if not member.bot
    }

    print(f"[Discord] Human Members : {len(discord_members)}")

    # ======================================================
    # Database Users
    # ======================================================

    print("\n[Database] Loading user_db...")

    rows = await get_all_users(guild.id)
    print(type(rows))

    if rows:
        print(type(rows[0]))
        print(rows[0])

    db_users = {
        row[0]
        for row in rows
    }

    print(f"[Database] Users : {len(db_users)}")

    # ======================================================
    # Find New Members
    # ======================================================

    print("\n------------------------------------------------------------")
    print("[SYNC] Finding new members...")

    new_users = []

    total = len(discord_members)

    for index, user_id in enumerate(discord_members.keys(), start=1):

        if index % 100 == 0 or index == total:
            print(f"[SYNC] Progress {index}/{total}")

        if user_id not in db_users:
            new_users.append(user_id)

    print(f"[SYNC] Need insert : {len(new_users)}")

    # ======================================================
    # Bulk Insert
    # ======================================================

    if new_users:

        print("[SYNC] Bulk inserting...")

        await ensure_users_exist(
            guild.id,
            new_users
        )

        print("[SYNC] Bulk insert finished.")

    # ======================================================
    # Find Orphan Users
    # ======================================================

    print("\n------------------------------------------------------------")
    print("[VERIFY] Checking orphan users...")

    orphan = []

    total = len(db_users)

    discord_ids = set(discord_members.keys())

    for index, user_id in enumerate(db_users, start=1):

        if index % 100 == 0 or index == total:
            print(f"[VERIFY] Progress {index}/{total}")

        if user_id not in discord_ids:
            orphan.append(user_id)

    print(f"[VERIFY] Orphan : {len(orphan)}")

    # ======================================================
    # Summary
    # ======================================================

    print("\n============================================================")
    print("[Check FINISHED]")

    print(f"Discord Members : {len(discord_members)}")
    print(f"Database Users  : {len(db_users)}")
    print(f"Added           : {len(new_users)}")
    print(f"Orphan Users    : {len(orphan)}")

    print("============================================================")

    return {
        "discord": len(discord_members),
        "database": len(db_users),
        "added": new_users,
        "orphan": orphan,
    }
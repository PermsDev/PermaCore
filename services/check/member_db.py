import discord

from database.user_manager import (
    get_all_users,
    sync_users,
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

    discord_members = [
        member
        for member in guild.members
        if not member.bot
    ]

    discord_ids = {
        member.id
        for member in discord_members
    }

    print(f"[Discord] Human Members : {len(discord_members)}")

    # ======================================================
    # Database Users
    # ======================================================

    print("\n[Database] Loading user_db...")

    rows = await get_all_users(guild.id)

    db_users = {
        row[0]      # gunakan row["user_id"] jika get_all_users memakai DictCursor
        for row in rows
    }

    print(f"[Database] Users Before : {len(db_users)}")

    # ======================================================
    # Sync Semua Member
    # ======================================================

    print("\n------------------------------------------------------------")
    print("[SYNC] Synchronizing members...")

    total = len(discord_members)

    for index, member in enumerate(discord_members, start=1):

        if index % 100 == 0 or index == total:
            print(f"[SYNC] Progress {index}/{total}")

    await sync_users(
        guild.id,
        discord_members
    )

    print("[SYNC] Synchronization finished.")

    # ======================================================
    # Added Members
    # ======================================================

    added = list(discord_ids - db_users)

    # ======================================================
    # Orphan Users
    # ======================================================

    print("\n------------------------------------------------------------")
    print("[VERIFY] Checking orphan users...")

    orphan = list(db_users - discord_ids)

    for index, user_id in enumerate(orphan, start=1):
        print(f"[{index}/{len(orphan)}] Orphan : {user_id}")

    # ======================================================
    # Summary
    # ======================================================

    database_after = len(db_users) + len(added)

    print("\n============================================================")
    print("[Check FINISHED]")
    print(f"Discord Members : {len(discord_members)}")
    print(f"Database Before : {len(db_users)}")
    print(f"Database After  : {database_after}")
    print(f"Added           : {len(added)}")
    print(f"Orphan Users    : {len(orphan)}")
    print("============================================================")

    return {
        "discord": len(discord_members),
        "database_before": len(db_users),
        "database_after": database_after,
        "added": added,
        "orphan": orphan,
    }
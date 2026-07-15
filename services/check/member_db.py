import asyncio
import discord

from database.user_manager import (
    get_all_users,
    ensure_user_exists,
)


async def check_member_db(
    guild: discord.Guild
):
    print("\n" + "=" * 60)
    print("[Check] START member_db scan")

    # ======================================================
    # LOAD DISCORD MEMBERS
    # ======================================================

    print("\n[Discord] Loading guild members...")

    discord_members = {
        member.id: member
        for member in guild.members
        if not member.bot
    }

    print(f"[Discord] Human Members : {len(discord_members)}")

    # ======================================================
    # LOAD DATABASE USERS
    # ======================================================

    print("\n[Database] Loading user_db...")

    rows = await get_all_users(guild.id)

    db_users = {
        row["user_id"]
        for row in rows
    }

    print(f"[Database] Users : {len(db_users)}")

    # ======================================================
    # DISCORD -> DATABASE
    # ======================================================

    print("\n" + "-" * 60)
    print("[SYNC] Discord -> Database")

    added = []

    total = len(discord_members)

    for index, (user_id, member) in enumerate(discord_members.items(), start=1):

        # Progress setiap 100 member
        if index % 100 == 0 or index == total:
            print(f"[SYNC] Progress {index}/{total}")

        if user_id in db_users:
            await asyncio.sleep(0)
            continue

        print(f"➕ Adding {member} ({user_id})")

        await ensure_user_exists(
            guild.id,
            user_id
        )

        added.append(user_id)

        await asyncio.sleep(0)

    print(f"[SYNC] Finished. Added {len(added)} members.")

    # ======================================================
    # DATABASE -> DISCORD
    # ======================================================

    print("\n" + "-" * 60)
    print("[VERIFY] Database -> Discord")

    orphan = []

    total = len(db_users)

    for index, user_id in enumerate(db_users, start=1):

        if index % 100 == 0 or index == total:
            print(f"[VERIFY] Progress {index}/{total}")

        if user_id in discord_members:
            await asyncio.sleep(0)
            continue

        print(f"❌ Orphan User : {user_id}")

        orphan.append(user_id)

        await asyncio.sleep(0)

    print(f"[VERIFY] Finished. Found {len(orphan)} orphan users.")

    # ======================================================
    # SUMMARY
    # ======================================================

    print("\n" + "=" * 60)
    print("[Check FINISHED]")

    print(f"Discord Members : {len(discord_members)}")
    print(f"Database Users  : {len(db_users)}")
    print(f"Added           : {len(added)}")
    print(f"Orphan Users    : {len(orphan)}")
    print("=" * 60)

    return {
        "discord": len(discord_members),
        "database": len(db_users),
        "added": added,
        "orphan": orphan,
    }
import discord

from database.role_manager import get_roles
from database.dm_message_manager import (
    get_dm_message,
    delete_dm_message,
    upsert_dm_message
)


# =========================
# VERIFIED SYSTEM (DB FLOW)
# =========================
async def handle_verified(member: discord.Member):

    guild = member.guild
    guild_id = guild.id
    user_id = member.id

    # =========================
    # LOAD ROLE CONFIG FROM DB
    # =========================
    roles = await get_roles(guild_id)

    verified_group = roles.get("by_group", {}).get("verified", {})
    pangkat_group = roles.get("by_group", {}).get("pangkat", {})

    # verified_role_id = verified_group.get("verified_role")
    verified_intro_id = verified_group.get("verified_intro")
    residents_role_id = pangkat_group.get("residents")

    if not all([verified_intro_id, residents_role_id]):
    # if not all([verified_role_id, verified_intro_id, residents_role_id]):
        print("[VERIFIED] Missing role configuration")
        return

    member_role_ids = {role.id for role in member.roles}

    # =========================
    # DEBUG STATUS
    # =========================
    # has_verified = verified_role_id in member_role_ids
    has_intro = verified_intro_id in member_role_ids

    # =========================
    # SAFETY CHECK
    # =========================
    if not has_intro:
    # if not (has_verified and has_intro):
        print(f"[VERIFIED] {member} not fully verified yet")
        return

    # =========================
    # DM TRANSITION SYSTEM
    # =========================
    try:
        dm_channel = await member.create_dm()

        # =========================
        # DELETE "JOINED" DM
        # =========================
        joined_dm_id = await get_dm_message(
            guild_id,
            user_id,
            "joined"
        )

        if joined_dm_id:
            try:
                old_msg = await dm_channel.fetch_message(joined_dm_id)
                await old_msg.delete()
            except (discord.NotFound, discord.Forbidden):
                pass
            except Exception as e:
                print(f"[VERIFIED] failed delete joined DM: {e}")

            await delete_dm_message(
                guild_id,
                user_id,
                "joined"
            )

        # =========================
        # SEND WELCOME DM (ANTI DUPLICATE)
        # =========================
        existing_welcome = await get_dm_message(
            guild_id,
            user_id,
            "welcome"
        )

        if not existing_welcome:

            welcome_text = (
                f"## Selamat datang di server {member.guild.name}! <a:hi_man:1478080922883719238>\n\n"
                f"🎉 Kamu sudah berhasil menyelesaikan proses verifikasi!\n\n"
                f"Sekarang kamu resmi menjadi bagian dari komunitas ini.\n"
                f"Silakan mulai berinteraksi, join event, dan nikmati fitur server.\n\n"
                f"Jika butuh bantuan, jangan ragu hubungi staff ya!"
            )

            new_msg = await dm_channel.send(welcome_text)

            await upsert_dm_message(
                guild_id,
                user_id,
                "welcome",
                new_msg.id
            )

        else:
            print(f"[VERIFIED] welcome DM already exists for {member}")

    except Exception as e:
        print(f"[VERIFIED] DM FLOW ERROR: {e}")

    # =========================
    # GIVE RESIDENTS ROLE
    # =========================
    try:
        residents_role = discord.utils.get(
            guild.roles,
            id=residents_role_id
        )

        if not residents_role:
            print("[VERIFIED] Residents role not found")
            return

        if residents_role in member.roles:
            print(f"[VERIFIED] {member} already has Residents")
            return

        await member.add_roles(
            residents_role,
            reason="User completed verification"
        )

        print(f"[VERIFIED] Residents added to {member}")

    except discord.Forbidden:
        print("[VERIFIED] Missing permission to add role")

    except Exception as e:
        print(f"[VERIFIED] Failed to add residents role: {e}")
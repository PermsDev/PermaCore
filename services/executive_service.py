import discord
import os
import json

from dotenv import load_dotenv

from views.executive_replace_view import ReplaceExecutiveView
from views.executive_info_view import ExecutiveInfoView
from utils.executive_embeds import get_executive_welcome_embed

from utils.logger import send_log
from utils.json_manager import (
    load_json,
    INTRO_DATA_PATH,
    DM_MESSAGES_PATH,
    save_json
)

load_dotenv()

EXECUTIVE_ROLES = {
    "guild": int(os.getenv("EXECUTIVE_GUILD_ROLE_ID")),
    "clan": int(os.getenv("EXECUTIVE_CLAN_ROLE_ID")),
    "sinyalid": int(os.getenv("EXECUTIVE_SINYALID_ROLE_ID")),
}

EXECUTIVE_CONFIG = {
    "guild": {
        "game_key": "growtopia",
        "emoji": "❄️"
    },

    "clan": {
        "game_key": "pw",
        "emoji": "🔆"
    },
    "sinyalid": {
        "game_key": "growtopia",
        "emoji": "📶"
    }
}

# =========================
# GET USER INTRO DATA
# =========================
async def get_user_intro_data(guild_id: int, user_id: int):

    data = await load_json(INTRO_DATA_PATH)
    guild_data = data.get(str(guild_id), {})
    
    return guild_data.get(str(user_id))

# =========================
# APPLY EXECUTIVE
# =========================
async def apply_executive(
    member: discord.Member,
    role: discord.Role,
    new_nickname: str
):

    # remove semua role executive lama
    for role_id in EXECUTIVE_ROLES.values():
        
        old_role = member.guild.get_role(role_id)

        if old_role and old_role in member.roles:
            await member.remove_roles(old_role)

    # add role baru
    await member.add_roles(role)

    # update nickname
    await member.edit(
        nick=new_nickname
    )

# =========================
# REFRESH EXECUTIVE DM
# =========================
async def refresh_executive_dm(
    guild: discord.Guild,
    member: discord.Member,
    executive_type: str,
    role: discord.Role,
    actor: discord.Member | discord.User
):

    dm_data = await load_json(DM_MESSAGES_PATH)

    guild_id = str(guild.id)
    user_id = str(member.id)

    # =========================
    # HAPUS DM LAMA
    # =========================
    old_dm_id = (
        dm_data
        .get(guild_id, {})
        .get(user_id, {})
        .get("executive_dm_id")
    )

    if old_dm_id:

        try:
            dm_channel = await member.create_dm()
            old_message = await dm_channel.fetch_message(old_dm_id)

            await old_message.delete()

        except Exception as e:

            await send_log(
                guild=guild,
                log_type="ERROR",
                action="Delete Executive DM",
                emoji="❌",
                user=actor,
                details={
                    "Target": member.mention,
                    "Error": str(e)
                }
            )

    # =========================
    # SEND DM BARU
    # =========================
    try:

        welcome_embed = get_executive_welcome_embed(
            member=member,
            role=role
        )

        dm_message = await member.send(
            embed=welcome_embed,
            view=ExecutiveInfoView(
                executive_type=executive_type
            )
        )

        if guild_id not in dm_data:
            dm_data[guild_id] = {}

        if user_id not in dm_data[guild_id]:
            dm_data[guild_id][user_id] = {}

        dm_data[guild_id][user_id][
            "executive_dm_id"
        ] = dm_message.id

        await save_json(DM_MESSAGES_PATH, dm_data)

    except Exception as e:

        await send_log(
            guild=guild,
            log_type="ERROR",
            action="Executive DM",
            emoji="❌",
            user=actor,
            details={
                "Target": member.mention,
                "Error": f"Gagal mengirim DM: {e}"
            }
        )

# =========================
# AREA UNTUK ADD EXECUTIVE ROLE
# =========================
async def add_executive_role(
    interaction: discord.Interaction,
    member: discord.Member,
    executive_type: str
):

    role_id = EXECUTIVE_ROLES.get(executive_type)

    if not role_id:

        await interaction.followup.send(
            "Jenis executive tidak valid.",
            ephemeral=True
        )
        return

    role = interaction.guild.get_role(role_id)

    if not role:
        
        await interaction.followup.send(
            "Role tidak ditemukan.",
            ephemeral=True
        )
        return

    # =========================
    # CEK APAKAH SUDAH PUNYA EXECUTIVE
    # =========================
    has_executive = False

    for role_id in EXECUTIVE_ROLES.values():
        
        old_role = interaction.guild.get_role(role_id)
        
        if old_role and old_role in member.roles:
            
            # jika role sama
            if old_role.id == role.id:
                
                await interaction.followup.send(
                    f"{member.mention} sudah memiliki role {role.mention}",
                    ephemeral=True
                )
                return

            has_executive = True
            break

    # =========================
    # AMBIL DATA INTRO
    # =========================
    intro_data = await get_user_intro_data(
        interaction.guild.id,
        member.id
    )
    
    if not intro_data:
        
        await interaction.followup.send(
            "Data intro user tidak ditemukan.",
            ephemeral=True
        )
        
        await send_log(
            guild=interaction.guild,
            log_type="ERROR",
            action="Add Executive",
            emoji="❌",
            user=interaction.user,
            details={
                "Target": member.mention,
                "Executive Type": executive_type,
                "Error": "user target belum mengisi intro"
            }
        )
        return

    config = EXECUTIVE_CONFIG.get(executive_type)

    if not config:

        await interaction.followup.send(
            "Config executive tidak ditemukan.",
            ephemeral=True
        )
        return

    game_key = config["game_key"]
    emoji = config["emoji"]

    game_data = intro_data.get(
        "games",
        {}
    ).get(game_key)

    if not game_data:

        await interaction.followup.send(
            f"Data game `{game_key}` tidak ditemukan.",
            ephemeral=True
        )
        await send_log(
            guild=interaction.guild,
            log_type="ERROR",
            action="Add Executive",
            emoji="❌",
            user=interaction.user,
            details={
                "Target": member.mention,
                "Executive Type": executive_type,
                "Error": f"user tidak mengisi data game {game_key}"
            }
        )
        return

    game_value = game_data.get("value")

    if not game_value:

        await interaction.followup.send(
            "Value game kosong.",
            ephemeral=True
        )
        
        await send_log(
            guild=interaction.guild,
            log_type="ERROR",
            action="Add Executive",
            emoji="❌",
            user=interaction.user,
            details={
                "Target": member.mention,
                "Executive Type": executive_type,
                "Error": f"value game {game_key} kosong"
            }
        )
        return

    # =========================
    # NICKNAME BARU
    # =========================
    new_nickname = f"{game_value} {emoji}"

    try:

        # =========================
        # JIKA SUDAH PUNYA EXECUTIVE
        # =========================
        if has_executive:

            embed = discord.Embed(
                title="⚠️ Executive Sudah Ada",
                description=(
                    f"{member.mention} sudah memiliki "
                    f"role executive lain.\n\n"
                    f"Apakah ingin menggantinya "
                    f"menjadi {role.mention}?"
                ),
                color=discord.Color.orange()
            )

            view = ReplaceExecutiveView(
                member=member,
                role=role,
                new_nickname=new_nickname,
                apply_callback=apply_executive,
                executive_type=executive_type
            )

            await interaction.followup.send(
                embed=embed,
                view=view,
                ephemeral=True
            )
            # ======================
            # LOG WARNING            
            # ======================
            await send_log(
                guild=interaction.guild,
                log_type="WARNING",
                action="Replace Executive",
                emoji="⚠️",
                user=interaction.user,
                details={
                    "Target": member.mention,
                    "New Role": role.mention,
                    "Nickname": new_nickname,
                    "Status": "User sudah memiliki executive lain"
                }
            )

            return

        # =========================
        # APPLY EXECUTIVE BARU
        # =========================
        await apply_executive(
            member=member,
            role=role,
            new_nickname=new_nickname
        )
        
        # =========================
        # REFRESH DM
        # =========================
        await refresh_executive_dm(
            guild=interaction.guild,
            member=member,
            executive_type=executive_type,
            role=role,
            actor=interaction.user
        )

        embed = discord.Embed(
            title="✅ Executive Added",
            description=(
                f"Berhasil menambahkan role "
                f"{role.mention}\n"
                f"ke {member.mention}\n\n"
                f"Nickname diubah menjadi:\n"
                f"`{new_nickname}`"
            ),
            color=discord.Color.green()
        )

        await interaction.followup.send(
            embed=embed,
            ephemeral=True
        )
            
        # ======================
        # LOG AKTIVITAS
        # ======================
        await send_log(
            guild=interaction.guild,
            log_type="SUCCESS",
            action="Add Executive",
            emoji="✅",
            user=interaction.user,
            details={
                "Target": member.mention,
                "Executive Type": executive_type,
            }
        )

    except Exception as e:

        await interaction.followup.send(
            f"Gagal menambahkan role.\n```{e}```",
            ephemeral=True
        )
        await send_log(
            guild=interaction.guild,
            log_type="ERROR",
            action="Add Executive",
            emoji="❌",
            user=interaction.user,
            details={
                "Target": member.mention,
                "Executive Type": executive_type,
                "Error": "gagal menambahkan role"
            }
        )


# =========================
# AREA UNTUK REMOVE EXECUTIVE ROLE
# =========================
async def remove_executive_role(
    interaction: discord.Interaction,
    member: discord.Member
):

    removed_roles = []

    try:

        # =========================
        # REMOVE SEMUA ROLE EXECUTIVE
        # =========================
        for role_id in EXECUTIVE_ROLES.values():

            role = interaction.guild.get_role(role_id)
            if role and role in member.roles:

                await member.remove_roles(role)

                removed_roles.append(
                    role.mention
                )

        # =========================
        # AMBIL NICKNAME ASLI
        # =========================
        intro_data = await get_user_intro_data(
            interaction.guild.id,
            member.id
        )

        if intro_data:

            original_nickname = intro_data.get(
                "nickname"
            )

            if original_nickname:

                await member.edit(
                    nick=original_nickname
                )

        # =========================
        # EMBED SUCCESS
        # =========================
        embed = discord.Embed(
            title="🗑️ Executive Removed",
            description=(
                f"Berhasil menghapus seluruh "
                f"role executive dari "
                f"{member.mention}\n\n"

                f"Role dihapus:\n"

                f"{', '.join(removed_roles) if removed_roles else 'Tidak ada'}\n\n"

                f"Nickname dikembalikan."
            ),
            color=discord.Color.red()
        )
        
        # ======================
        # HAPUS DM MESSAGE JIKA ADA
        # ======================
        dm_data = await load_json(DM_MESSAGES_PATH)

        guild_id = str(interaction.guild.id)
        user_id = str(member.id)

        executive_dm_id = (
            dm_data
            .get(guild_id, {})
            .get(user_id, {})
            .get("executive_dm_id")
        )

        if executive_dm_id:

            try:

                dm_channel = await member.create_dm()

                dm_message = await dm_channel.fetch_message(
                    executive_dm_id
                )

                await dm_message.delete()

                # hapus data setelah delete
                del dm_data[guild_id][user_id][
                    "executive_dm_id"
                ]

                await save_json(DM_MESSAGES_PATH, dm_data)

            except Exception as e:

                await send_log(
                    guild=interaction.guild,
                    log_type="ERROR",
                    action="Delete Executive DM",
                    emoji="❌",
                    user=interaction.user,
                    details={
                        "Target": member.mention,
                        "Error": str(e)
                    }
                )

        await interaction.followup.send(
            embed=embed,
            ephemeral=True
        )
        await send_log(
            guild=interaction.guild,
            log_type="SUCCESS",
            action="Remove Executive",
            emoji="🗑️",
            user=interaction.user,
            details={
                "Target": member.mention
            }
        )

    except Exception as e:

        await interaction.followup.send(
            f"Gagal menghapus executive.\n```{e}```",
            ephemeral=True
        )
        await send_log(
            guild=interaction.guild,
            log_type="ERROR",
            action="Remove Executive",
            emoji="❌",
            user=interaction.user,
            details={
                "Target": member.mention,
                "Error": str(e)
            }
        )
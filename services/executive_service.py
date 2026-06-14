import discord

from views.executive_replace_view import ReplaceExecutiveView
from views.executive_info_view import ExecutiveInfoView
from utils.executive_embeds import get_executive_welcome_embed
from utils.logger import send_log

from database.role_manager import get_roles
from database.intro_manager import get_user_profile
from database.dm_message_manager import (
    get_dm_message,
    upsert_dm_message,
    delete_dm_message
)

# =========================
# ROLE LOADER (FROM DB)
# =========================
def get_executive_roles(guild_id: int):
    roles = get_roles(guild_id)
    return roles.get("by_group", {}).get("executive", {})

# =========================
# EXECUTIVE ROLES (Logic Only)
# =========================

EXECUTIVE_CONFIG = {
    "executive_guild": {
        "game_key": "growtopia",
        "emoji": "❄️"
    },
    "executive_clan": {
        "game_key": "pw",
        "emoji": "🔆"
    },
    "executive_sinyalid": {
        "game_key": "growtopia",
        "emoji": "📶"
    }
}

# =========================
# GET USER INTRO DATA
# =========================
async def get_user_intro_data(guild_id: int, user_id: int):
    return get_user_profile(guild_id, user_id)

# =========================
# RESOLVE ROLE (IMPORTANT)
# =========================
def resolve_executive_role(guild_id: int, executive_type: str):
    exec_roles = get_executive_roles(guild_id)
    config = EXECUTIVE_CONFIG.get(executive_type)

    if not config:
        return None, None

    role_id = exec_roles.get(config["role_key"])
    return role_id, config

# =========================
# APPLY EXECUTIVE
# =========================
async def apply_executive(member: discord.Member, role: discord.Role, new_nickname: str):
    
    exec_roles = get_executive_roles(member.guild.id)

    # remove semua role executive lama
    for role_id in exec_roles.values():
        old_role = member.guild.get_role(role_id)

        if old_role and old_role in member.roles:
            await member.remove_roles(old_role)

    # add role baru
    await member.add_roles(role)

    # update nickname
    try:
        await member.edit(nick=new_nickname)

    except discord.Forbidden:
        await send_log(
            guild=member.guild,
            log_type="ERROR",
            action="Apply Executive",
            emoji="❌",
            user=member,
            details={"Error": "Tidak ada izin ubah nickname"}
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

    # =========================
    # HAPUS DM LAMA (MYSQL)
    # =========================
    old_dm_id = get_dm_message(guild.id, member.id, "executive")

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
        embed = get_executive_welcome_embed(member=member, role=role)
        dm_message = await member.send(
            embed=embed,
            view=ExecutiveInfoView(executive_type=executive_type)
        )

        upsert_dm_message(
            guild.id,
            member.id,
            "executive",
            dm_message.id
        )

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
# ADD EXECUTIVE ROLE
# =========================
async def add_executive_role(
    interaction: discord.Interaction,
    member: discord.Member,
    executive_type: str
):

    role_id, config = resolve_executive_role(
        interaction.guild.id, 
        executive_type
    )

    if not role_id or not config:
        await interaction.followup.send(
            "❌ Config executive tidak valid.",
            ephemeral=True
        )
        return

    role = interaction.guild.get_role(role_id)

    if not role:
        await interaction.followup.send(
            "❌ Role tidak ditemukan.",
            ephemeral=True
        )
        return

    # cek executive lama
    exec_roles = get_executive_roles(interaction.guild.id)
    has_executive = False

    for rid in exec_roles.values():
        old_role = interaction.guild.get_role(rid)

        if old_role and old_role in member.roles:
            if old_role.id == role.id:
                await interaction.followup.send(
                    f"{member.mention} sudah memiliki role {role.mention}",
                    ephemeral=True
                )
                return

            has_executive = True
            break

    intro_data = await get_user_intro_data(interaction.guild.id, member.id)

    if not intro_data:
        await interaction.followup.send(
            "❌ Data intro tidak ditemukan.",
            ephemeral=True
        )
        return

    game_data = intro_data.get("games", {}).get(config["game_key"])

    if not game_data or not game_data.get("value"):
        await interaction.followup.send(
            "❌ Data game tidak ditemukan.",
            ephemeral=True
        )
        return

    new_nickname = f"{game_data['value']} {config['emoji']}"

    try:

        if has_executive:

            embed = discord.Embed(
                title="⚠️ Executive Already Exists",
                description=f"{member.mention} sudah punya executive lain. Ganti?",
                color=discord.Color.orange()
            )

            view = ReplaceExecutiveView(
                member=member,
                role=role,
                new_nickname=new_nickname,
                apply_callback=apply_executive,
                executive_type=executive_type
            )

            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            return

        await apply_executive(member, role, new_nickname)

        await refresh_executive_dm(
            guild=interaction.guild,
            member=member,
            executive_type=executive_type,
            role=role,
            actor=interaction.user
        )

        await interaction.followup.send(
            embed=discord.Embed(
                title="✅ Executive Added",
                description=f"{member.mention} → {role.mention}",
                color=discord.Color.green()
            ),
            ephemeral=True
        )

    except Exception as e:
        await interaction.followup.send(f"❌ Error:\n```{e}```", ephemeral=True)

# =========================
# REMOVE EXECUTIVE ROLE
# =========================
async def remove_executive_role(
    interaction: discord.Interaction,
    member: discord.Member
):

    exec_roles = get_executive_roles(interaction.guild.id)
    removed = []

    try:

        for rid in exec_roles.values():
            role = interaction.guild.get_role(rid)

            if role and role in member.roles:
                await member.remove_roles(role)
                removed.append(role.mention)

        intro_data = await get_user_intro_data(interaction.guild.id, member.id)

        if intro_data:
            nick = intro_data.get("nickname")
            if nick:
                try:
                    await member.edit(nick=nick)
                except discord.Forbidden:
                    pass

        old_dm_id = get_dm_message(interaction.guild.id, member.id, "executive")

        if old_dm_id:
            try:
                dm = await member.create_dm()
                msg = await dm.fetch_message(old_dm_id)
                await msg.delete()
            except:
                pass

            delete_dm_message(interaction.guild.id, member.id, "executive")

        await interaction.followup.send(
            embed=discord.Embed(
                title="🗑️ Executive Removed",
                description=f"Removed: {', '.join(removed) or 'None'}",
                color=discord.Color.red()
            ),
            ephemeral=True
        )

    except Exception as e:
        await interaction.followup.send(f"❌ Error:\n```{e}```", ephemeral=True)
        
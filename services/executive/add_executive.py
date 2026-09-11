import discord

from views.executive.roles.executive_replace_view import ReplaceExecutiveView
from views.executive.message.executive_info_view import ExecutiveInfoView
from views.executive.message.executive_embeds import (
    get_executive_welcome_embed
)

from utils.logger import send_log

from database.core.role_manager import get_roles
from database.core.intro_manager import get_user_intro

from database.core.dm_message_manager import (
    get_dm_message,
    upsert_dm_message
)


# =========================
# ROLE LOADER
# =========================

async def get_executive_roles(
    guild_id: int
):
    roles = await get_roles(
        guild_id
    )

    return roles.get(
        "by_group",
        {}
    ).get(
        "executive",
        {}
    )


# =========================
# EXECUTIVE CONFIG
# =========================

EXECUTIVE_CONFIG = {
    "executive_guild": {
        "role_key": "executive_guild",
        "game_key": "growtopia"
    },

    "executive_sinyalid": {
        "role_key": "executive_sinyalid",
        "game_key": "growtopia"
    }
}


# =========================
# RESOLVE EXECUTIVE ROLE
# =========================

async def resolve_executive_role(
    guild_id: int,
    executive_type: str
):

    exec_roles = await get_executive_roles(
        guild_id
    )

    config = EXECUTIVE_CONFIG.get(
        executive_type
    )

    if not config:
        return None, None

    role_id = exec_roles.get(
        config["role_key"]
    )

    return role_id, config


# =========================
# APPLY EXECUTIVE
# =========================

async def apply_executive(
    member: discord.Member,
    role: discord.Role
):

    exec_roles = await get_executive_roles(
        member.guild.id
    )

    # =========================
    # REMOVE EXECUTIVE LAMA
    # =========================

    for role_id in exec_roles.values():

        old_role = member.guild.get_role(
            role_id
        )

        if old_role and old_role in member.roles:

            await member.remove_roles(
                old_role,
                reason="Replacing executive role"
            )

    # =========================
    # ADD EXECUTIVE BARU
    # =========================

    await member.add_roles(
        role,
        reason="Executive role added"
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
    # BOT ID
    # =========================

    bot_id = guild.me.id

    # =========================
    # HAPUS DM LAMA
    # =========================

    old_dm_id = await get_dm_message(
        guild_id=guild.id,
        user_id=member.id,
        bot_id=bot_id,
        dm_type="executive"
    )

    if old_dm_id:

        try:

            dm_channel = await member.create_dm()

            old_message = await dm_channel.fetch_message(
                old_dm_id
            )

            await old_message.delete()

        except discord.NotFound:
            pass

        except discord.Forbidden as e:

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
    # KIRIM DM BARU
    # =========================

    try:

        embed = get_executive_welcome_embed(
            member=member,
            role=role
        )

        dm_message = await member.send(
            embed=embed,
            view=ExecutiveInfoView(
                executive_type=executive_type
            )
        )

        await upsert_dm_message(
            guild_id=guild.id,
            user_id=member.id,
            bot_id=bot_id,
            dm_type="executive",
            message_id=dm_message.id
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

    # =========================
    # RESOLVE ROLE
    # =========================

    role_id, config = await resolve_executive_role(
        interaction.guild.id,
        executive_type
    )

    if not role_id or not config:

        await interaction.followup.send(
            "❌ Config executive tidak valid.",
            ephemeral=True
        )

        return

    role = interaction.guild.get_role(
        role_id
    )

    if not role:

        await interaction.followup.send(
            "❌ Role tidak ditemukan.",
            ephemeral=True
        )

        return

    # =========================
    # CEK EXECUTIVE LAMA
    # =========================

    exec_roles = await get_executive_roles(
        interaction.guild.id
    )

    has_executive = False

    for rid in exec_roles.values():

        old_role = interaction.guild.get_role(
            rid
        )

        if old_role and old_role in member.roles:

            if old_role.id == role.id:

                await interaction.followup.send(
                    f"{member.mention} sudah memiliki role "
                    f"{role.mention}",
                    ephemeral=True
                )

                return

            has_executive = True
            break

    # =========================
    # VALIDASI INTRO
    # =========================

    intro_data = await get_user_intro(
        member.id
    )

    if not intro_data:

        await interaction.followup.send(
            "❌ Data intro tidak ditemukan.",
            ephemeral=True
        )

        return

    # =========================
    # VALIDASI GAME
    # =========================

    game_data = next(
        (
            intro
            for intro in intro_data
            if intro["game_key"] == config["game_key"]
        ),
        None
    )

    if not game_data or not game_data.get("value"):

        await interaction.followup.send(
            "❌ Data game tidak ditemukan.",
            ephemeral=True
        )

        return

    # =========================
    # APPLY
    # =========================

    try:

        # =========================
        # SUDAH PUNYA EXECUTIVE
        # =========================

        if has_executive:

            embed = discord.Embed(
                title="⚠️ Executive Already Exists",
                description=(
                    f"{member.mention} sudah punya "
                    "executive lain. Ganti?"
                ),
                color=discord.Color.orange()
            )

            view = ReplaceExecutiveView(
                member=member,
                role=role,
                apply_callback=apply_executive,
                executive_type=executive_type
            )

            await interaction.followup.send(
                embed=embed,
                view=view,
                ephemeral=True
            )

            return

        # =========================
        # ADD ROLE
        # =========================

        await apply_executive(
            member=member,
            role=role
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

        # =========================
        # RESPONSE
        # =========================

        await interaction.followup.send(
            embed=discord.Embed(
                title="✅ Executive Added",
                description=(
                    f"{member.mention} → "
                    f"{role.mention}"
                ),
                color=discord.Color.green()
            ),
            ephemeral=True
        )

    except Exception as e:

        await send_log(
            guild=interaction.guild,
            log_type="ERROR",
            action="Add Executive",
            emoji="❌",
            user=interaction.user,
            details={
                "Target": member.mention,
                "Error": str(e)
            }
        )

        await interaction.followup.send(
            f"❌ Error:\n```{e}```",
            ephemeral=True
        )
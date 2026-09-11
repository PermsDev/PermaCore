import discord

from utils.logger import send_log

from database.core.role_manager import get_roles
from database.main.user.member_manager import get_nickname
from database.core.dm_message_manager import (
    get_dm_message,
    delete_dm_message
)


# =========================
# ROLE LOADER
# =========================

async def get_executive_roles(
    guild_id: int
) -> dict:

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
# REMOVE EXECUTIVE ROLE
# =========================

async def remove_executive_role(
    interaction: discord.Interaction,
    member: discord.Member
):

    guild = interaction.guild

    if guild is None:
        await interaction.followup.send(
            "❌ Command hanya dapat digunakan di server.",
            ephemeral=True
        )
        return

    # =========================
    # BOT ID
    # =========================

    bot_id = guild.me.id

    exec_roles = await get_executive_roles(
        guild.id
    )

    removed = []

    try:

        # =========================
        # REMOVE EXECUTIVE ROLES
        # =========================

        for role_id in exec_roles.values():

            role = guild.get_role(
                role_id
            )

            if role and role in member.roles:

                await member.remove_roles(
                    role,
                    reason="Executive role removed"
                )

                removed.append(
                    role.mention
                )

        # =========================
        # GET NICKNAME
        # =========================

        nickname = await get_nickname(
            member.id
        )

        # =========================
        # RESTORE NICKNAME
        # =========================

        if nickname:

            try:

                await member.edit(
                    nick=nickname,
                    reason="Restore nickname after executive removal"
                )

            except discord.Forbidden:

                await send_log(
                    guild=guild,
                    log_type="WARNING",
                    action="Remove Executive",
                    emoji="⚠️",
                    user=interaction.user,
                    details={
                        "Target": member.mention,
                        "Error": "Tidak ada izin mengubah nickname"
                    }
                )

            except discord.HTTPException as e:

                await send_log(
                    guild=guild,
                    log_type="WARNING",
                    action="Remove Executive",
                    emoji="⚠️",
                    user=interaction.user,
                    details={
                        "Target": member.mention,
                        "Error": str(e)
                    }
                )

        # =========================
        # DELETE EXECUTIVE DM
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

            except discord.Forbidden:

                await send_log(
                    guild=guild,
                    log_type="WARNING",
                    action="Delete Executive DM",
                    emoji="⚠️",
                    user=interaction.user,
                    details={
                        "Target": member.mention,
                        "Error": "Tidak dapat menghapus DM"
                    }
                )

            except discord.HTTPException as e:

                await send_log(
                    guild=guild,
                    log_type="WARNING",
                    action="Delete Executive DM",
                    emoji="⚠️",
                    user=interaction.user,
                    details={
                        "Target": member.mention,
                        "Error": str(e)
                    }
                )

            # =========================
            # DELETE DB RECORD
            # =========================

            await delete_dm_message(
                guild_id=guild.id,
                user_id=member.id,
                bot_id=bot_id,
                dm_type="executive"
            )

        # =========================
        # RESPONSE
        # =========================

        await interaction.followup.send(
            embed=discord.Embed(
                title="🗑️ Executive Removed",
                description=(
                    f"{member.mention}\n\n"
                    f"**Removed:** "
                    f"{', '.join(removed) if removed else 'None'}"
                ),
                color=discord.Color.red()
            ),
            ephemeral=True
        )

    except discord.Forbidden as e:

        await send_log(
            guild=guild,
            log_type="ERROR",
            action="Remove Executive",
            emoji="❌",
            user=interaction.user,
            details={
                "Target": member.mention,
                "Error": str(e)
            }
        )

        await interaction.followup.send(
            "❌ Bot tidak memiliki permission untuk menghapus role executive.",
            ephemeral=True
        )

    except discord.HTTPException as e:

        await send_log(
            guild=guild,
            log_type="ERROR",
            action="Remove Executive",
            emoji="❌",
            user=interaction.user,
            details={
                "Target": member.mention,
                "Error": str(e)
            }
        )

        await interaction.followup.send(
            f"❌ Discord API Error:\n```{e}```",
            ephemeral=True
        )

    except Exception as e:

        await send_log(
            guild=guild,
            log_type="ERROR",
            action="Remove Executive",
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
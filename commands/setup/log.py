import asyncio

import discord

from database.channel_manager import (
    set_channel
)


async def setup_log(
    interaction: discord.Interaction,
    channel: discord.TextChannel
):
    """
    Setup log channel.
    """

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            "Tidak ada permission!",
            ephemeral=True
        )
        return

    # =====================================
    # Simpan database
    # =====================================
    await set_channel(
        interaction.guild.id,
        "LOG_CHANNEL",
        channel.id
    )

    # =====================================
    # Response
    # =====================================

    embed = discord.Embed(
        title="✅ Log Channel Updated",
        description=(
            f"Channel log berhasil "
            f"diatur ke {channel.mention}"
        ),
        color=discord.Color.orange()
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )
import discord

from views.guild.guild_panel import create_guild_manage_panel


async def setup_guildManage(
    bot,
    interaction: discord.Interaction,
    channel: discord.TextChannel
):
    """
    Setup guild management panel.
    """

    # =====================================
    # CEK PERMISSION ADMIN
    # =====================================

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            "Tidak ada permission!",
            ephemeral=True
        )
        return

    # =====================================
    # KIRIM PANEL
    # =====================================

    await channel.send(
        embed=create_guild_manage_panel()
    )

    # =====================================
    # RESPONSE
    # =====================================

    await interaction.response.send_message(
        f"Panel Guild Management dibuat di {channel.mention}"
    )
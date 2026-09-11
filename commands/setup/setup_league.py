import discord

from views.League.embed.panel import create_league_panel


async def setup_league(
    bot,
    interaction: discord.Interaction,
    channel: discord.TextChannel
):
    """
    Setup league panel.
    """

    # =====================================
    # Cek permission admin
    # =====================================

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            "Tidak ada permission!",
            ephemeral=True
        )
        return

    # =====================================
    # Kirim panel
    # =====================================

    await channel.send(
        embed=create_league_panel()
    )

    # =====================================
    # Response
    # =====================================

    await interaction.response.send_message(
        f"Panel League dibuat di {channel.mention}"
    )
import discord

from views.league.embed.panel import create_top_score_panel
from views.league.views.top_score import TopScoreView


async def setup_league(
    bot,
    interaction: discord.Interaction,
    channel: discord.TextChannel
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "Tidak ada permission!",
            ephemeral=True
        )
        return

    embed = await create_top_score_panel()

    await channel.send(
        embed=embed,
        view=TopScoreView()
    )

    await interaction.response.send_message(
        f"Panel League dibuat di {channel.mention}"
    )
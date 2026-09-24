import discord

from database.guild.event_clash_score_manager import (
    get_top_total_score,
    get_top_monthly_score
)


class TopScoreView(discord.ui.View):

    def __init__(
        self,
        timeout: float | None = 300
    ):
        super().__init__(timeout=timeout)

    @discord.ui.button(
        label="Refresh",
        style=discord.ButtonStyle.primary,
        emoji="🔄"
    )
    async def refresh(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        total_scores = await get_top_total_score()
        monthly_scores = await get_top_monthly_score()

        from views.league.embed.top_score import (
            create_top_score_embed
        )

        await interaction.response.edit_message(
            embed=create_top_score_embed(
                total_scores,
                monthly_scores
            ),
            view=self
        )
import discord


class PrizeTopScoreButton(
    discord.ui.Button
):

    def __init__(self):

        super().__init__(
            label="Prize Top Score",
            style=discord.ButtonStyle.secondary,
            custom_id="league:prize_top_score"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        view = discord.ui.LayoutView(
            timeout=None
        )

        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    "## 🏆 Prize Top Score\n"
                    "Information about Top Score prizes."
                )
            )
        )

        view.add_item(container)

        await interaction.response.send_message(
            view=view,
            ephemeral=True
        )
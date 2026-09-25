import discord


class MoreTotalScoreButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="More",
            style=discord.ButtonStyle.secondary,
            custom_id="league_more_total_score"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Total Score More diklik.",
            ephemeral=True
        )


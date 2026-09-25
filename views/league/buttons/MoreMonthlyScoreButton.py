import discord

class MoreMonthlyScoreButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="More",
            style=discord.ButtonStyle.secondary,
            custom_id="league_more_monthly_score"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Monthly Score More diklik.",
            ephemeral=True
        )
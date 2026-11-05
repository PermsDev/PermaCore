import discord

from database.core.emoji_manager import get_emoji
from views.guild.league.reward.reward_view import RewardTopScoreView


class RewardTopScoreButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Reward Top Score",
            emoji=get_emoji("GoldGuildChest"),
            style=discord.ButtonStyle.secondary,
            custom_id="league:reward_top_score"
        )

    async def callback(self, interaction: discord.Interaction):

        await interaction.response.send_message(
            view=RewardTopScoreView(),
            ephemeral=True
        )
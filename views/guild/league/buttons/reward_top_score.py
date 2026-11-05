import discord
import logging

from database.core.emoji_manager import get_emoji
from views.guild.league.reward.reward_view import RewardTopScoreView

logger = logging.getLogger(__name__)


class RewardTopScoreButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Reward Top Score",
            emoji=get_emoji("GoldGuildChest"),
            style=discord.ButtonStyle.secondary,
            custom_id="league:reward_top_score"
        )

    async def callback(self, interaction: discord.Interaction):

        logger.info("[Reward Top Score] Interaction received")

        try:
            await interaction.response.defer(
                ephemeral=True,
                thinking=True
            )

            logger.info("[Reward Top Score] Interaction deferred")

            view = await RewardTopScoreView.create()

            logger.info("[Reward Top Score] View created")

            await interaction.followup.send(
                view=view,
                ephemeral=True
            )

            logger.info("[Reward Top Score] Response sent")

        except Exception:
            logger.exception("[Reward Top Score] Failed")
import discord
import logging

from database.core.emoji_manager import get_emoji
from views.guild.league.reward.reward_view import ClashRewardView

logger = logging.getLogger(__name__)


class ClashRewardButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Clash Reward",
            emoji=get_emoji("GoldGuildChest"),
            style=discord.ButtonStyle.secondary,
            custom_id="league:clash_reward"
        )

    async def callback(self, interaction: discord.Interaction):

        logger.info("[Clash Reward] Interaction received")

        try:
            await interaction.response.defer(
                ephemeral=True,
                thinking=True
            )

            logger.info("[Clash Reward] Interaction deferred")

            view = await ClashRewardView.create()

            logger.info("[Clash Reward] View created")

            await interaction.followup.send(
                view=view,
                ephemeral=True
            )

            logger.info("[Clash Reward] Response sent")

        except Exception:
            logger.exception("[Clash Reward] Failed")
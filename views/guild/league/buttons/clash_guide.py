import discord

from database.core.emoji_manager import get_emoji
from views.guild.league.guide.clash_guide import ClashGuideView


class ClashGuideButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Clash Guide",
            emoji=get_emoji("guide"),
            style=discord.ButtonStyle.secondary,
            custom_id="league:clash_guide"
        )

    async def callback(self, interaction: discord.Interaction):

        await interaction.response.send_message(
            view=ClashGuideView(),
            ephemeral=True
        )
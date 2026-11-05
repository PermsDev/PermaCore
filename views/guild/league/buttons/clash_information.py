import discord

from database.core.emoji_manager import get_emoji
from views.guild.league.information.clash_information import ClashInformationView


class ClashInformationButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Clash Information",
            emoji=get_emoji("ScrollBulletin"),
            style=discord.ButtonStyle.secondary,
            custom_id="league:clash_information"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        view = ClashInformationView()

        await interaction.response.send_message(
            view=view,
            ephemeral=True
        )
import discord

from views.intro.panel.intro_modal import IntroModal
from database.main.user_game_manager import get_user_profile_for_modal


class IntroButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Profile",
            style=discord.ButtonStyle.green,
            emoji="🪪",
            custom_id="intro_button"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        guild_id = interaction.guild.id
        user_id = interaction.user.id

        user_data = await get_user_profile_for_modal(
            guild_id,
            user_id
        )

        await interaction.response.send_modal(
            IntroModal(user_data)
        )
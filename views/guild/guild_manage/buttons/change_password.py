import discord

from database.core.emoji_manager import get_emoji
from views.guild.guild_manage.modals import ChangePasswordModal

class ChangePasswordButton(discord.ui.Button):

    def __init__(self):

        super().__init__(
            label="Change Password",
            emoji=get_emoji("password_door"),
            style=discord.ButtonStyle.primary,
            custom_id="guild_manage:change_password"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.send_modal(
            ChangePasswordModal()
        )
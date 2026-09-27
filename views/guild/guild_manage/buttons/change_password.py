import discord

from database.core.emoji_manager import get_emoji

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

        await interaction.response.send_message(
            "Fitur Change Password belum tersedia.",
            ephemeral=True
        )
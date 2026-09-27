import discord

from database.core.emoji_manager import get_emoji

class ChangeDoorPasswordButton(discord.ui.Button):

    def __init__(self):

        super().__init__(
            label="Change Password Door",
            emoji=get_emoji("password_door"),
            style=discord.ButtonStyle.primary,
            custom_id="guild_manage:change_door_password"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.send_message(
            "Fitur Change Door Password belum tersedia.",
            ephemeral=True
        )
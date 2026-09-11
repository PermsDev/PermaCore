import discord

from views.intro.display_name.display_name_view import DisplayNameView


class DisplayNameButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Display Name",
            style=discord.ButtonStyle.primary,
            emoji="🏷️",
            custom_id="display_name_button"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.send_message(
            "Pilih display name yang ingin digunakan:",
            view=DisplayNameView(),
            ephemeral=True
        )
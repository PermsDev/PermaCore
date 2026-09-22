import discord

from views.guild.modals import TopClashModal


class TopClashButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Top Clash",
            emoji="🏆",
            style=discord.ButtonStyle.primary,
            custom_id="guild_manage:top_clash"
        )

    async def callback(self, interaction: discord.Interaction):

        await interaction.response.send_modal(
            TopClashModal()
        )
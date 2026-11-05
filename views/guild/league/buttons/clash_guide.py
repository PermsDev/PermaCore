import discord

from database.core.emoji_manager import get_emoji


class ClashGuideButton(
    discord.ui.Button
):

    def __init__(self):

        super().__init__(
            label="Clash Guide",
            emoji=get_emoji("guide"),
            style=discord.ButtonStyle.secondary,
            custom_id="league:clash_guide"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        view = discord.ui.LayoutView(
            timeout=None
        )

        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    "## 📖 Clash Guide\n"
                    "Information about how to participate in Clash."
                )
            )
        )

        view.add_item(container)

        await interaction.response.send_message(
            view=view,
            ephemeral=True
        )
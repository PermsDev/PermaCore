import discord


class ClashInformationButton( 
    discord.ui.Button
):

    def __init__(self):

        super().__init__(
            label="Clash Information",
            style=discord.ButtonStyle.secondary,
            custom_id="league:clash_information"
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
                    "## ⚔️ Clash Information\n"
                    "Information about PermaClash."
                )
            )
        )

        view.add_item(container)

        await interaction.response.send_message(
            view=view,
            ephemeral=True
        )
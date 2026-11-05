import discord

from database.core.emoji_manager import get_emoji


class ClashInformationView(discord.ui.LayoutView):

    def __init__(self):
        super().__init__(timeout=None)

        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    "## " + get_emoji("ScrollBulletin") + " Clash Information\n"
                    "Information about PermaClash."
                )
            )
        )

        self.add_item(container)
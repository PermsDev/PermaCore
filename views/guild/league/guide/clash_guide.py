import discord

from database.core.emoji_manager import get_emoji


class ClashGuideView(discord.ui.LayoutView):

    def __init__(self):
        super().__init__(timeout=None)

        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    "## " + get_emoji('guide') + " Clash Guide\n"
                    "Information about how to participate in Clash."
                )
            )
        )

        self.add_item(container)
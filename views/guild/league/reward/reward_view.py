import discord

from database.core.emoji_manager import get_emoji


class RewardTopScoreView(discord.ui.LayoutView):

    def __init__(self):
        super().__init__(timeout=None)

        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    "## " + get_emoji('GoldGuildChest') + " Reward Top Score\n"
                    "Information about Top Score rewards."
                )
            )
        )

        self.add_item(container)
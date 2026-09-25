import discord

from views.league.buttons import (
    MoreTotalScoreButton,
    MoreMonthlyScoreButton
)


class TopScoreView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(
            MoreTotalScoreButton()
        )

        self.add_item(
            MoreMonthlyScoreButton()
        )
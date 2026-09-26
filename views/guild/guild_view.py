import discord

from views.guild.guild_manage.buttons import TopClashButton
from views.guild.league.buttons import (
    MoreTotalScoreButton,
    MoreMonthlyScoreButton
)


class GuildManageView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(
            TopClashButton()
        )
        
class GuildClashView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(
            MoreTotalScoreButton()
        )
        self.add_item(
            MoreMonthlyScoreButton()
        )
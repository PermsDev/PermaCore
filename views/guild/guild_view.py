import discord

from views.guild.buttons import TopClashButton


class GuildManageView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(
            TopClashButton()
        )
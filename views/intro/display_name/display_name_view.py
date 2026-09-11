import discord

from views.intro.display_name.display_name_select import (
    DisplayNameSelect
)


class DisplayNameView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

        self.add_item(
            DisplayNameSelect()
        )
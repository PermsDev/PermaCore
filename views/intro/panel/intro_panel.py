import discord

from views.intro.panel.intro_button import IntroButton
from views.intro.display_name.display_name_button import DisplayNameButton


class IntroPanel(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(
            IntroButton()
        )

        self.add_item(
            DisplayNameButton()
        )
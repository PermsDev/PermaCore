import discord

from database.main.game_manager import get_user_id_by_game_value
from views.guild.views.top_clash import TopClashView


class TopClashModal(discord.ui.Modal, title="Event Clash - Top 5"):

    top_1 = discord.ui.TextInput(
        label="GrowID Top 1 Clash",
        placeholder="Masukkan GrowID Top 1",
        required=True,
        max_length=50
    )

    top_2 = discord.ui.TextInput(
        label="GrowID Top 2 Clash",
        placeholder="Masukkan GrowID Top 2",
        required=True,
        max_length=50
    )

    top_3 = discord.ui.TextInput(
        label="GrowID Top 3 Clash",
        placeholder="Masukkan GrowID Top 3",
        required=True,
        max_length=50
    )

    top_4 = discord.ui.TextInput(
        label="GrowID Top 4 Clash",
        placeholder="Masukkan GrowID Top 4",
        required=True,
        max_length=50
    )

    top_5 = discord.ui.TextInput(
        label="GrowID Top 5 Clash",
        placeholder="Masukkan GrowID Top 5",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):

        growids = [
            self.top_1.value.strip(),
            self.top_2.value.strip(),
            self.top_3.value.strip(),
            self.top_4.value.strip(),
            self.top_5.value.strip()
        ]

        user_ids = []

        for growid in growids:
            user_id = await get_user_id_by_game_value(
                "growtopia",
                growid
            )

            user_ids.append(user_id)

        view = TopClashView(
            growids=growids,
            user_ids=user_ids,
            owner_id=interaction.user.id
        )

        await interaction.response.send_message(
            view.get_content(),
            view=view,
            ephemeral=True
        )


class TopClashEditModal(
    discord.ui.Modal,
    title="Edit Event Clash - Top 5"
):

    def __init__(self, view: TopClashView):

        super().__init__()

        self.view = view

        self.top_1 = discord.ui.TextInput(
            label="GrowID Top 1 Clash",
            required=True,
            max_length=50,
            default=view.growids[0]
        )

        self.top_2 = discord.ui.TextInput(
            label="GrowID Top 2 Clash",
            required=True,
            max_length=50,
            default=view.growids[1]
        )

        self.top_3 = discord.ui.TextInput(
            label="GrowID Top 3 Clash",
            required=True,
            max_length=50,
            default=view.growids[2]
        )

        self.top_4 = discord.ui.TextInput(
            label="GrowID Top 4 Clash",
            required=True,
            max_length=50,
            default=view.growids[3]
        )

        self.top_5 = discord.ui.TextInput(
            label="GrowID Top 5 Clash",
            required=True,
            max_length=50,
            default=view.growids[4]
        )

        self.add_item(self.top_1)
        self.add_item(self.top_2)
        self.add_item(self.top_3)
        self.add_item(self.top_4)
        self.add_item(self.top_5)

    async def on_submit(self, interaction: discord.Interaction):

        growids = [
            self.top_1.value.strip(),
            self.top_2.value.strip(),
            self.top_3.value.strip(),
            self.top_4.value.strip(),
            self.top_5.value.strip()
        ]

        user_ids = []

        for growid in growids:
            user_id = await get_user_id_by_game_value(
                "growtopia",
                growid
            )

            user_ids.append(user_id)

        self.view.growids = growids
        self.view.user_ids = user_ids

        await interaction.response.edit_message(
            content=self.view.get_content(),
            view=self.view
        )
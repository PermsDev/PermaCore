import discord

from database.guild.event_clash_manager import get_current_top_clash
from database.core.emoji_manager import get_emoji
from views.guild.guild_manage.modals import TopClashModal


class TopClashButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Top Clash",
            emoji=get_emoji("rank_1"),
            style=discord.ButtonStyle.primary,
            custom_id="guild_manage:top_clash"
        )

    async def callback(self, interaction: discord.Interaction):

        results = await get_current_top_clash()

        growids = ["", "", "", "", ""]
        user_ids = [None, None, None, None, None]

        for result in results:
            rank = result["rank_position"]

            if 1 <= rank <= 5:
                index = rank - 1

                growids[index] = result["growid"] or ""
                user_ids[index] = result["user_id"]

        await interaction.response.send_modal(
            TopClashModal(
                growids=growids,
                user_ids=user_ids
            )
        )
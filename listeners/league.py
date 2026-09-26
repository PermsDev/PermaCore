import os

import aiohttp
import discord
from discord.ext import commands

from views.guild.league.embed.panel import create_top_score_panel


class LeagueListener(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(
        self,
        interaction: discord.Interaction
    ):
        if interaction.type != discord.InteractionType.component:
            return

        data = interaction.data

        if not data:
            return

        custom_id = data.get("custom_id")

        if custom_id != "league_select_series":
            return

        values = data.get("values")

        if not values:
            return

        try:
            series_id = int(values[0])
        except (ValueError, TypeError):
            await interaction.response.send_message(
                "Series tidak valid.",
                ephemeral=True
            )
            return

        try:
            await interaction.response.defer()

            components = await create_top_score_panel(
                series_id=series_id
            )

            token = os.getenv("TOKEN")

            url = (
                f"https://discord.com/api/v10/"
                f"channels/{interaction.channel_id}/"
                f"messages/{interaction.message.id}"
            )

            headers = {
                "Authorization": f"Bot {token}",
                "Content-Type": "application/json"
            }

            payload = {
                "components": components,
                "flags": 32768
            }

            async with aiohttp.ClientSession() as session:
                async with session.patch(
                    url,
                    headers=headers,
                    json=payload
                ) as response:

                    if response.status >= 400:
                        error = await response.text()
                        raise RuntimeError(
                            f"Discord API {response.status}: {error}"
                        )

        except Exception as e:
            import traceback

            print(
                f"[League] Gagal mengganti series: {e}"
            )

            traceback.print_exc()

            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "Gagal memuat data series.",
                    ephemeral=True
                )


async def setup(bot):
    await bot.add_cog(
        LeagueListener(bot)
    )

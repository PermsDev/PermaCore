import discord

from discord import app_commands
from discord.ext import commands


class Ping(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="ping",
        description="Menampilkan latency bot."
    )
    async def ping(
        self,
        interaction: discord.Interaction
    ):
        await interaction.response.defer(ephemeral=True)

        latency = round(self.bot.latency * 1000)

        await interaction.edit_original_response(
            content=f"🏓 **Pong!**\nLatency: `{latency} ms`"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Ping(bot))
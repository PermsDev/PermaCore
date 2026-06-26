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

        latency = round(
            self.bot.latency * 1000
        )

        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"**Latency:** `{latency} ms`",
            color=discord.Color.green()
        )

        embed.set_footer(
            text="PermaCore"
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(
        Ping(bot)
    )
import os
import discord

from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands

load_dotenv()

GUILD_ID = int(os.getenv("GUILD_ID"))

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="ping",
        description="Cek apakah bot hidup"
    )
    async def ping(
        self,
        interaction: discord.Interaction
    ):
        await interaction.response.send_message(
            "Pong!"
        )

async def setup(bot):

    guild = discord.Object(
        id=GUILD_ID
    )

    await bot.add_cog(
        Ping(bot),
        guilds=[guild]
    )
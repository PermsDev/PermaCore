import discord

from utils.logger import send_log
from database.guild_manager import add_guild


async def handle_guild_join(guild: discord.Guild):
    await add_guild(guild.id, guild.name)

    print(f"Bot bergabung ke server: {guild.name} ({guild.id})")
import discord

from database.guild_manager import remove_guild
from utils.logger import send_log


async def handle_guild_remove(guild: discord.Guild):

    print(f"Bot keluar dari server: {guild.name} ({guild.id})")

    # Hapus guild dari database
    remove_guild(guild.id)

    # (Opsional) Logging
    # await send_log(...)
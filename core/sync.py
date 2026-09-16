import discord

from database.main.guild_key_manager import get_guild_ids
from services.bots.env_service import is_development


async def sync_commands(bot):

    guild_ids = await get_guild_ids("Main")

    if not guild_ids:
        print("[Sync] Tidak ada guild dengan guild_key='Main'.")
        return

    for guild_id in guild_ids:

        guild = discord.Object(id=guild_id)

        # Copy semua global command ke guild
        bot.tree.copy_global_to(guild=guild)

        # Sync command ke guild
        synced = await bot.tree.sync(
            guild=guild
        )

        if is_development():
            print(
                f"[Sync] Guild -> {guild_id} "
                f"({len(synced)} Commands)"
            )

    # Hapus command global dari local tree
    bot.tree.clear_commands(guild=None)

    # Sinkronkan penghapusan global ke Discord
    global_synced = await bot.tree.sync()

    if is_development():
        print(
            f"[Sync] Global -> ({len(global_synced)} Commands)"
        )
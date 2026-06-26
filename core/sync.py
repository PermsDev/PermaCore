import discord
from discord.ext import commands
from database.guild_key_manager import get_guild_ids


# ==================================================
# PUBLIC
# ==================================================
async def sync_public_commands(bot: commands.Bot):
    """
    Sync seluruh Public Commands secara Global.
    """

    print("[Sync] Syncing Public Commands...")

    synced = await bot.tree.sync()

    print(f"[Sync] Synced {len(synced)} Public Commands.")


# ==================================================
# MAIN
# ==================================================
async def sync_main_commands(bot: commands.Bot):

    print("[Sync] Syncing Main Commands...")

    guild_ids = get_guild_ids("Main")

    for guild_id in guild_ids:

        guild = discord.Object(id=guild_id)

        bot.tree.copy_global_to(
            guild=guild
        )

        synced = await bot.tree.sync(
            guild=guild
        )

        print(
            f"[Sync] Main -> {guild_id} ({len(synced)} Commands)"
        )
import discord
from discord.ext import commands
from database.guild_key_manager import get_guild_ids
from database.guild_manager import get_all_guild_ids


# ==================================================
# PUBLIC
# ==================================================
async def sync_public_commands(bot: commands.Bot):

    guild_ids = await get_all_guild_ids()

    for guild_id in guild_ids:

        guild = discord.Object(id=guild_id)

        synced = await bot.tree.sync(guild=guild)

        print(
            f"[Sync] Public -> {guild_id} ({len(synced)} Commands)"
        )

# ==================================================
# MAIN
# ==================================================
async def sync_main_commands(bot: commands.Bot):

    print("[Sync] Syncing Main Commands...")

    guild_ids = await get_guild_ids("Main")

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
        
async def sync_partner_growtopia_commands(bot: commands.Bot):

    print("[Sync] Syncing Patner Growtopia Commands...")

    guild_ids = await get_guild_ids("Partner_Growtopia")

    for guild_id in guild_ids:

        guild = discord.Object(id=guild_id)

        bot.tree.copy_global_to(
            guild=guild
        )

        synced = await bot.tree.sync(
            guild=guild
        )

        print(
            f"[Sync] Partner Growtopia -> {guild_id} ({len(synced)} Commands)"
        )
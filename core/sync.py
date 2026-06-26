import os
import discord

from dotenv import load_dotenv
from discord.ext import commands

# ======================
# LOAD ENV
# ======================
load_dotenv()

GUILD_ID = int(os.getenv("GUILD_ID"))


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
    """
    Sync seluruh Main Commands ke guild utama.
    """

    print("[Sync] Syncing Main Commands...")

    guild = discord.Object(id=GUILD_ID)

    bot.tree.copy_global_to(
        guild=guild
    )

    synced = await bot.tree.sync(
        guild=guild
    )

    print(f"[Sync] Synced {len(synced)} Main Commands.")
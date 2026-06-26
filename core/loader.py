import os
from discord.ext import commands


async def _load_folder(bot: commands.Bot, folder: str):
    """
    Load semua extension (.py) secara recursive dari folder tertentu.
    """

    for root, _, files in os.walk(folder):

        for filename in files:

            # hanya file python
            if not filename.endswith(".py"):
                continue

            # skip private/helper file
            if filename.startswith("_"):
                continue

            path = os.path.join(root, filename)

            module = (
                os.path.relpath(path, ".")
                .replace("\\", ".")
                .replace("/", ".")
                .removesuffix(".py")
            )

            await bot.load_extension(module)

            print(f"[Loader] Loaded: {module}")


# ==================================================
# PUBLIC
# ==================================================

async def load_public_cogs(bot: commands.Bot):
    """
    Load semua cog Public.
    """

    print("[Loader] Loading Public Cogs...")

    await _load_folder(
        bot,
        "./cogs/Public"
    )

    print("[Loader] Public Cogs Loaded.")


# ==================================================
# MAIN
# ==================================================

async def load_main_cogs(bot: commands.Bot):
    """
    Load semua cog Main.
    """

    print("[Loader] Loading Main Cogs...")

    await _load_folder(
        bot,
        "./cogs/Main"
    )

    print("[Loader] Main Cogs Loaded.")
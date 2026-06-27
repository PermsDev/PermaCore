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


async def _unload_folder(bot: commands.Bot, folder: str):
    """
    Unload semua extension (.py) secara recursive dari folder tertentu.
    """

    modules = []

    for root, _, files in os.walk(folder):

        for filename in files:

            if not filename.endswith(".py"):
                continue

            if filename.startswith("_"):
                continue

            path = os.path.join(root, filename)

            module = (
                os.path.relpath(path, ".")
                .replace("\\", ".")
                .replace("/", ".")
                .removesuffix(".py")
            )

            modules.append(module)

    # unload dari paling dalam
    for module in sorted(modules, reverse=True):
        await bot.unload_extension(module)

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

async def unload_public_cogs(bot: commands.Bot):

    print("[Loader] Unloading Public Cogs...")

    await _unload_folder(
        bot,
        "./cogs/Public"
    )


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

async def unload_main_cogs(bot: commands.Bot):

    print("[Loader] Unloading Main Cogs...")

    await _unload_folder(
        bot,
        "./cogs/Main"
    )
    
# ==================================================
# Partner Growtopia
# ==================================================

async def load_partner_growtopia_cogs(bot: commands.Bot):
    """
    Load semua cog Partner Growtopia.
    """

    print("[Loader] Loading Partner Growtopia Cogs...")

    await _load_folder(
        bot,
        "./cogs/Partner/Growtopia"
    )

async def unload_partner_growtopia_cogs(bot: commands.Bot):

    print("[Loader] Unloading Partner Growtopia Cogs...")

    await _unload_folder(
        bot,
        "./cogs/Partner/Growtopia"
    )
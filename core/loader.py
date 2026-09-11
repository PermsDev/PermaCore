import os

from discord.ext import commands


COGS_FOLDER = "./cogs"


async def load_cogs(bot: commands.Bot):
    """
    Load semua extension (.py) secara recursive dari folder cogs.
    """

    print("[Loader] Loading Cogs...")

    for root, _, files in os.walk(COGS_FOLDER):

        for filename in files:

            # Hanya file Python
            if not filename.endswith(".py"):
                continue

            # Skip private/helper file
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

            # print(f"[Loader] Loaded: {module}")
import discord

from database.main.guild_key_manager import get_guild_ids
from services.bots import is_development


async def sync_commands(bot):

    # =====================================
    # AMBIL GUILD DENGAN KEY MAIN
    # =====================================

    main_guild_ids = await get_guild_ids("Main")

    main_guild_ids = {
        int(guild_id)
        for guild_id in main_guild_ids
    }

    # =====================================
    # CEK GUILD YANG BOT SEDANG IKUTI
    # =====================================

    for guild in bot.guilds:

        # =====================================
        # GUILD TIDAK MEMILIKI KEY MAIN
        # =====================================

        if guild.id not in main_guild_ids:

            if is_development():

                print(
                    f"[Sync] Skip -> {guild.name} "
                    f"({guild.id}) "
                    f"[Tidak memiliki guild_key='Main']"
                )

            continue

        # =====================================
        # GUILD MEMILIKI KEY MAIN
        # =====================================

        guild_object = discord.Object(
            id=guild.id
        )

        # =====================================
        # COPY GLOBAL COMMAND KE GUILD
        # =====================================

        bot.tree.copy_global_to(
            guild=guild_object
        )

        # =====================================
        # SYNC COMMAND
        # =====================================

        try:

            synced = await bot.tree.sync(
                guild=guild_object
            )

            if is_development():

                print(
                    f"[Sync] Guild -> {guild.name} "
                    f"({guild.id}) "
                    f"({len(synced)} Commands)"
                )

        except discord.Forbidden:

            print(
                f"[Sync] Missing Access -> "
                f"{guild.name} ({guild.id})"
            )

        except discord.HTTPException as e:

            print(
                f"[Sync] HTTP Error -> "
                f"{guild.name} ({guild.id}) -> {e}"
            )

    # =====================================
    # HAPUS COMMAND GLOBAL DARI LOCAL TREE
    # =====================================

    bot.tree.clear_commands(
        guild=None
    )

    # =====================================
    # HAPUS COMMAND GLOBAL DI DISCORD
    # =====================================

    try:

        global_synced = await bot.tree.sync()

        if is_development():

            print(
                f"[Sync] Global -> "
                f"({len(global_synced)} Commands)"
            )

    except discord.HTTPException as e:

        print(
            f"[Sync] Global HTTP Error -> {e}"
        )
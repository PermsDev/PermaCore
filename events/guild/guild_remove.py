import discord

from database.main.bots.bot_guild_manager import remove_bot_from_guild


async def handle_guild_remove(
    bot: discord.Client,
    guild: discord.Guild
):
    print(
        f"Bot keluar dari server: "
        f"{guild.name} ({guild.id})"
    )

    # ======================
    # REMOVE BOT -> GUILD
    # ======================
    await remove_bot_from_guild(
        bot_id=bot.user.id,
        guild_id=guild.id
    )
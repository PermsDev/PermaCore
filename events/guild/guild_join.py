import discord

from database.main.guild_manager import add_guild
from database.main.bots.bot_guild_manager import add_bot_to_guild
from services.bots.user_sync import sync_guild_members


async def handle_guild_join(
    bot: discord.Client,
    guild: discord.Guild
):
    # ======================
    # REGISTER GUILD
    # ======================
    await add_guild(
        guild_id=guild.id,
        guild_name=guild.name
    )

    # ======================
    # REGISTER BOT -> GUILD
    # ======================
    await add_bot_to_guild(
        bot_id=bot.user.id,
        guild_id=guild.id
    )
    

    print(
        f"Bot bergabung ke server: "
        f"{guild.name} ({guild.id})"
    )
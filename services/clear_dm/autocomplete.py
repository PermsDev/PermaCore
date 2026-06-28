import discord
from discord import app_commands

from database.guild_manager import get_all_guilds


# ==================================================
# GUILD AUTOCOMPLETE
# ==================================================
async def guild_autocomplete(
    interaction: discord.Interaction,
    current: str
):

    guilds = await get_all_guilds()

    current = current.lower()

    choices = []

    for guild in guilds:

        guild_name = guild["nama_guild"] or str(guild["guild_id"])

        if current not in guild_name.lower():
            continue

        choices.append(
            app_commands.Choice(
                name=guild_name,
                value=str(guild["guild_id"])
            )
        )

        if len(choices) >= 25:
            break

    return choices
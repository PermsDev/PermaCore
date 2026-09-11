import discord

from database.main.user.user_manager import (
    ensure_users_exist
)


# ==================================================
# SYNC ONE GUILD
# ==================================================

async def sync_guild_members(
    guild: discord.Guild
):
    """
    Menambahkan seluruh member guild ke user_db.

    Hanya menyimpan:
        user_id

    Data lain seperti:
        nickname
        guild_id
        joined_at

    tidak disentuh di service ini.
    """

    if not guild.members:
        return

    user_ids = [
        member.id
        for member in guild.members
        if not member.bot
    ]

    if not user_ids:
        return

    await ensure_users_exist(user_ids)


# ==================================================
# SYNC ALL GUILDS
# ==================================================

async def sync_all_members(
    bot: discord.Client
):
    """
    Sinkronisasi seluruh member dari semua guild
    tempat bot berada.

    Hanya user_id yang dimasukkan ke user_db.
    """

    for guild in bot.guilds:

        await sync_guild_members(guild)
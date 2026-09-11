from database.main.bots.bot_manager import add_bot
from database.main.bots.bot_guild_manager import (
    get_guilds_by_bot,
    add_bot_to_guild,
    remove_bot_from_guild,
)
from database.main.guild_manager import add_guild


# ==================================================
# SYNC BOT GUILDS
# ==================================================
async def sync_bot_guilds(bot):
    """
    Sinkronisasi guild yang terdaftar pada Discord dengan database.

    Aturan:
        - Guild yang ada di Discord tetapi belum ada di database:
            -> tambahkan ke guild_db
            -> tambahkan ke bot_guild_db

        - Guild yang sudah ada di database tetapi bot sudah tidak
          berada di guild tersebut:
            -> hapus dari bot_guild_db

        - guild_db TIDAK PERNAH dihapus.
    """

    bot_id = bot.user.id

    # --------------------------------------------------
    # REGISTER BOT
    # --------------------------------------------------
    await add_bot(
        bot_id=bot_id,
        bot_name=bot.user.name
    )

    # --------------------------------------------------
    # GUILD YANG AKTUALNYA DIMASUKI BOT
    # --------------------------------------------------
    current_guilds = {
        guild.id: guild
        for guild in bot.guilds
    }

    # --------------------------------------------------
    # GUILD YANG TERCATAT UNTUK BOT INI
    # --------------------------------------------------
    registered_guilds = await get_guilds_by_bot(bot_id)

    registered_guild_ids = {
        guild["guild_id"]
        for guild in registered_guilds
    }

    # --------------------------------------------------
    # TAMBAHKAN GUILD YANG BARU
    # --------------------------------------------------
    for guild_id, guild in current_guilds.items():

        # guild_db hanya registry.
        # Tidak pernah dihapus.
        await add_guild(
            guild_id=guild.id,
            guild_name=guild.name
        )

        # Pastikan relasi bot <-> guild ada.
        if guild_id not in registered_guild_ids:
            await add_bot_to_guild(
                bot_id=bot_id,
                guild_id=guild_id
            )

    # --------------------------------------------------
    # HAPUS GUILD YANG SUDAH TIDAK DIMASUKI BOT
    # --------------------------------------------------
    for guild_id in registered_guild_ids:

        if guild_id not in current_guilds:
            await remove_bot_from_guild(
                bot_id=bot_id,
                guild_id=guild_id
            )
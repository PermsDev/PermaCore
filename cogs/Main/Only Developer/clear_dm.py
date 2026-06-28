import os
import discord

from discord.ext import commands
from discord import app_commands

from services.clear_dm.cleaner import clear_dm
from services.clear_dm.autocomplete import guild_autocomplete

OWNER_ID = int(os.getenv("OWNER_ID"))

class ClearDM(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ==================================================
    # CLEAR BOT DM
    # ==================================================
    @app_commands.command(
        name="clearbotdm",
        description="(Only Developer) Hapus DM bot."
    )
    @app_commands.autocomplete(
        guild=guild_autocomplete
    )
    @app_commands.check(
        lambda interaction:
        interaction.user.id == OWNER_ID
    )
    async def clear_bot_dm(

        self,
        interaction: discord.Interaction,

        guild: str | None = None,

        user: discord.Member | None = None

    ):

        await interaction.response.send_message(

            "Mulai menghapus DM bot...",

            ephemeral=True

        )

        try:

            result = await clear_dm(

                bot=self.bot,

                interaction=interaction,

                guild_id=guild,

                user=user

            )

            await interaction.followup.send(

                f"✅ Selesai Clear DM\n\n"

                f"Guild : {result['guild'].name}\n"

                f"Target User : {result['targets']}\n"

                f"Deleted : {result['deleted']}\n"

                f"Protected : {result['skipped']}\n"

                f"Failed : {result['failed']}",

                ephemeral=True

            )

        except Exception as e:

            await interaction.followup.send(

                f"❌ Gagal menjalankan Clear DM\n\n{e}",

                ephemeral=True

            )


async def setup(bot):
    await bot.add_cog(
        ClearDM(bot)
    )
import discord
import traceback

from discord import app_commands
from discord.ext import commands

from services.Partnership.Growtopia.introduction import gt_setup_introduction


class GTSetup(commands.GroupCog, group_name="gt_setup"):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="introduction",
        description="Set Growtopia introduction channel."
    )
    @app_commands.describe(
        channel="Channel target untuk introduction.",
        roles="Role yang diizinkan (opsional)."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def introduction(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        roles: discord.Role | None = None
    ):

        try:
            await gt_setup_introduction(
                interaction,
                channel,
                roles
            )

        except Exception:
            print("\n========== COMMAND ERROR ==========")
            traceback.print_exc()
            print("===================================\n")

            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Terjadi error. Silakan cek console.",
                    ephemeral=True
                )


async def setup(bot: commands.Bot):
    await bot.add_cog(GTSetup(bot))
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

from services.welcome import update_welcome_service


class Update(commands.GroupCog, name="update"):

    def __init__(self, bot):
        self.bot = bot

    # =========================
    # /update welcome
    # =========================
    @app_commands.command(
        name="welcome",
        description="Update welcome message"
    )
    @app_commands.default_permissions(
        administrator=True
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    @app_commands.describe(
        user="Optional user"
    )
    async def welcome(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.Member] = None
    ):

        await interaction.response.defer(
            ephemeral=True
        )

        result = await update_welcome_service(
            interaction=interaction,
            user=user
        )

        await interaction.followup.send(
            result,
            ephemeral=True
        )

    @welcome.error
    async def welcome_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        if isinstance(
            error,
            app_commands.MissingPermissions
        ):
            await interaction.response.send_message(
                "❌ Kamu harus memiliki permission Administrator.",
                ephemeral=True
            )
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Update(bot))
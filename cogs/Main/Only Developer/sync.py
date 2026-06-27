import os
import discord

from discord import app_commands
from discord.ext import commands

from core.loader import (
    load_public_cogs,
    unload_public_cogs,
    load_main_cogs,
    unload_main_cogs,
    load_partner_growtopia_cogs,
    unload_partner_growtopia_cogs
)

from core.sync import (
    sync_public_commands,
    sync_main_commands,
    sync_partner_growtopia_commands
)

OWNER_ID = int(os.getenv("OWNER_ID"))


class Sync(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="sync",
        description="Sync slash commands."
    )
    async def sync(self, interaction: discord.Interaction):

        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                "❌ Hanya owner yang dapat menggunakan command ini.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)
        
        await unload_public_cogs(self.bot)
        await unload_main_cogs(self.bot)
        await unload_partner_growtopia_cogs(self.bot)

        # PUBLIC
        await load_public_cogs(self.bot)
        await sync_public_commands(self.bot)
        await unload_public_cogs(self.bot)

        # MAIN
        await load_main_cogs(self.bot)
        await sync_main_commands(self.bot)
        await unload_main_cogs(self.bot)

        # PARTNER
        await load_partner_growtopia_cogs(self.bot)
        await sync_partner_growtopia_commands(self.bot)
        await unload_partner_growtopia_cogs(self.bot)
        
        # LOAD UNTUK RUNTIME
        await load_public_cogs(self.bot)
        await load_main_cogs(self.bot)
        await load_partner_growtopia_cogs(self.bot)

        await interaction.followup.send(
            "✅ Semua slash command berhasil di-sync.",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Sync(bot))
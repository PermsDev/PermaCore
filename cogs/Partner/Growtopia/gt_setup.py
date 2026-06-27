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
        channel="Channel target untuk introduction."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def introduction(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):

        print("\n========== /gt_setup introduction ==========")
        print(f"Guild        : {interaction.guild.name} ({interaction.guild.id})")
        print(f"User         : {interaction.user} ({interaction.user.id})")
        print(f"Channel      : {channel.name} ({channel.id})")
        print(f"Bot Admin    : {interaction.guild.me.guild_permissions.administrator}")

        perms = channel.permissions_for(interaction.guild.me)
        print(f"View Channel : {perms.view_channel}")
        print(f"Send Message : {perms.send_messages}")
        print(f"Embed Links  : {perms.embed_links}")
        print("============================================\n")

        try:
            await gt_setup_introduction(
                interaction,
                channel
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
    await bot.add_cog(
        GTSetup(bot)
    )
import discord
from discord.ext import commands
from discord import app_commands

from services.executive_service import remove_executive_role


class Remove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    remove = app_commands.Group(
        name="remove",
        description="Remove something",
        default_permissions=discord.Permissions(
            administrator=True
        )
    )

    @remove.command(
        name="executive",
        description="Remove all executive roles"
    )
    async def remove_executive(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):

        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "Tidak ada permission!",
                ephemeral=True
            )
            return

        await interaction.response.defer(
            ephemeral=True
        )

        await remove_executive_role(
            interaction=interaction,
            member=member
        )
        


async def setup(bot):
    await bot.add_cog(Remove(bot))
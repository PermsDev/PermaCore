import discord
from discord.ext import commands
from discord import app_commands

from services.executive.add_executive import (
    add_executive_role
)

from services.executive.remove_executive import (
    remove_executive_role
)


class Executive(commands.Cog):

    executive = app_commands.Group(
        name="executive",
        description="Manage executive"
    )

    def __init__(self, bot):
        self.bot = bot

    # ==================================================
    # /executive add
    # ==================================================

    @executive.command(
        name="add",
        description="Add executive role to member"
    )
    @app_commands.describe(
        executive_type="Jenis executive",
        member="Member yang akan diberikan role"
    )
    @app_commands.choices(
        executive_type=[
            app_commands.Choice(
                name="Guild Executive",
                value="executive_guild"
            ),
            app_commands.Choice(
                name="SinyalID Executive",
                value="executive_sinyalid"
            ),
        ]
    )
    async def add_executive(
        self,
        interaction: discord.Interaction,
        executive_type: app_commands.Choice[str],
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

        await add_executive_role(
            interaction=interaction,
            member=member,
            executive_type=executive_type.value
        )

    # ==================================================
    # /executive remove
    # ==================================================

    @executive.command(
        name="remove",
        description="Remove all executive roles from member"
    )
    @app_commands.describe(
        member="Member yang executive role-nya akan dihapus"
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
    await bot.add_cog(
        Executive(bot)
    )
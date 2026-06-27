import discord
from discord.ext import commands
from discord import app_commands

from services.executive_service import add_executive_role

class Add(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    add = app_commands.Group(
        name="add",
        description="Add something",
        default_permissions=discord.Permissions(
            administrator=True
        )
    )

    @add.command(
        name="executive",
        description="(Admin only) Add executive role to member"
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
                name="Clan Executive",
                value="executive_clan"
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

        await interaction.response.defer(ephemeral=True)

        await add_executive_role(
            interaction=interaction,
            member=member,
            executive_type=executive_type.value
        )

async def setup(bot):
    await bot.add_cog(Add(bot))
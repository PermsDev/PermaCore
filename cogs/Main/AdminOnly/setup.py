import discord
from discord import app_commands
from discord.ext import commands

from commands.setup.intro import setup_intro
from commands.setup.feedback import setup_feedback
from commands.setup.log import setup_log
from commands.setup.welcome import setup_welcome


# ======================
# COG
# ======================
class Setup(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    setup = app_commands.Group(
        name="setup",
        description="Setup server",
        default_permissions=discord.Permissions(
            administrator=True
        )
    )

    # ======================
    # SETUP INTRO
    # ======================
    @setup.command(name="intro", description="Set channel intro | Admin only")
    async def intro(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):

        await setup_intro(
            bot=self.bot,
            interaction=interaction,
            channel=channel
        )

    # ======================
    # SETUP FEEDBACK
    # ======================
    @setup.command(
        name="feedback",
        description="Setup feedback panel | Admin only"
    )
    async def feedback(
        self,
        interaction: discord.Interaction,
        panel_channel: discord.TextChannel,
        target_channel: discord.TextChannel
    ):

        await setup_feedback(
            bot=self.bot,
            interaction=interaction,
            panel_channel=panel_channel,
            target_channel=target_channel
        )

    # ======================
    # SETUP LOG
    # ======================
    @setup.command(
        name="log",
        description="Setup log channel | Admin only"
    )
    async def log(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):

        await setup_log(
            interaction=interaction,
            channel=channel
        )

    # ======================
    # SETUP WELCOME
    # ======================
    @setup.command(
        name="welcome",
        description="Setup welcome channel | Admin only"
    )
    async def welcome(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):

        await setup_welcome(
            interaction=interaction,
            channel=channel
        )


# ======================
# LOAD COG
# ======================
async def setup(bot):
    await bot.add_cog(
        Setup(bot)
    )
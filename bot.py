import os
import discord
from dotenv import load_dotenv
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

from utils.delete_scheduler import delete_checker

from views.intro import IntroButton, register_persistent_views
from views.feedback import FeedbackButton, ReplyView
from views.executive_info_view import ExecutiveInfoView

from database.database import init_database
from database.emoji_manager import load_emojis
from database.feedback_manager import get_pending_feedbacks
from database.role_manager import (
    get_roles,
    load_roles,
)

from events.guild_join import handle_guild_join
from events.guild_remove import handle_guild_remove

from events.member_join import handle_member_join
from events.member_remove import handle_member_remove
from events.member_verified import handle_verified
from events.member_role_update import (
    get_changed_roles,
    has_pangkat,
    has_role_group_change,
    process_welcome
)

# ======================
# LOAD ENV
# ======================
load_dotenv()
TOKEN = os.getenv("TOKEN")

# ======================
# INTENTS
# ======================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True


# ======================
# BOT CLASS
# ======================
class MyBot(commands.Bot):

    async def setup_hook(self):

        # ======================
        # INIT DATABASE (ASYNCMY)
        # ======================
        await init_database()

        # ======================
        # SYNC
        # ======================

        # await load_public_cogs(self)
        # await sync_public_commands(self)
        # await unload_public_cogs(self)

        # await load_main_cogs(self)
        # await sync_main_commands(self)
        # await unload_main_cogs(self)

        # await load_partner_growtopia_cogs(self)
        # await sync_partner_growtopia_commands(self)
        # await unload_partner_growtopia_cogs(self)

        # ======================
        # LOAD UNTUK RUNTIME
        # ======================

        await load_public_cogs(self)
        await load_main_cogs(self)
        await load_partner_growtopia_cogs(self)

        # ======================
        # PERSISTENT VIEWS
        # ======================
        self.add_view(IntroButton())
        self.add_view(FeedbackButton())

        self.add_view(ExecutiveInfoView("guild"))
        self.add_view(ExecutiveInfoView("clan"))
        self.add_view(ExecutiveInfoView("sinyalid"))

        await register_persistent_views(self)

        # ======================
        # RESTORE VIEWS
        # ======================
        pending_feedbacks = await get_pending_feedbacks()

        for feedback in pending_feedbacks:
            self.add_view(
                ReplyView(),
                message_id=feedback["message_id"]
            )


# ======================
# BOT INSTANCE
# ======================
bot = MyBot(
    command_prefix="!",
    intents=intents
)


# ======================
# ON READY
# ======================
@bot.event
async def on_ready():

    await load_emojis()

    bot.loop.create_task(delete_checker(bot))

    # preload role cache
    for guild in bot.guilds:
        await load_roles(guild.id)

    print(f"Bot login sebagai {bot.user}")


# ======================
# GUILD EVENTS
# ======================
@bot.event
async def on_guild_join(guild):
    await handle_guild_join(guild)


@bot.event
async def on_guild_remove(guild):
    await handle_guild_remove(guild)


# ======================
# MEMBER EVENTS
# ======================
@bot.event
async def on_member_join(member):

    if member.bot:
        return

    await handle_member_join(member)


@bot.event
async def on_member_remove(member):

    if member.bot:
        return

    await handle_member_remove(member)


@bot.event
async def on_member_update(before, after):

    if after.bot:
        return

    if before.roles == after.roles:
        return

    role_groups = await get_roles(after.guild.id)
    changed_roles = get_changed_roles(before, after)

    # VERIFY CHECK
    verified_roles = set(
        role_groups["by_group"]["verified"].values()
    )

    if changed_roles & verified_roles:
        await handle_verified(after)

    # WELCOME CHECK
    if has_pangkat(after, role_groups):

        if has_role_group_change(before, after, role_groups):
            await process_welcome(after)


# ======================
# RUN BOT
# ======================
bot.run(TOKEN)
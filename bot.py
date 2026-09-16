import logging
import os
import discord
import asyncio
from dotenv import load_dotenv
from discord.ext import commands

from core.loader import load_cogs
from core.sync import sync_commands

from services.bots.bot_guild_sync import sync_bot_guilds
from services.bots.env_service import is_production
from services.bots.user_sync import sync_all_members, sync_guild_members
from services.heartbeat import HeartbeatTask
from utils.delete_scheduler import delete_checker

from views.intro.copyValue.register import register_persistent_views
from views.feedback import FeedbackButton, ReplyView
from views.executive.message.executive_info_view import ExecutiveInfoView

from views.intro.panel.intro_panel import IntroPanel

from database.main.guild_key_manager import get_guild_ids, is_main_guild

from database.database import (
    init_database,
    close_database,
)

from database.core.emoji_manager import load_emojis
from database.core.feedback_manager import get_pending_feedbacks
from database.core.role_manager import (
    get_roles,
    load_roles,
)

from events.guild.guild_join import handle_guild_join
from events.guild.guild_remove import handle_guild_remove

from events.member_join import handle_member_join
from events.member_main_remove import handle_member_main_remove

from events.handlers.executive_nickname import (
    handle_executive_nickname
)

from events.member_remove import handle_member_remove_database
from events.member_role_update import (
    has_pangkat,
    has_role_group_change,
    process_welcome
)

# ======================
# LOAD ENV
# ======================
load_dotenv()
TOKEN = os.getenv("TOKEN")
HEARTBEAT_CHECK = os.getenv("HEALTH_CHECKS")

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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.heartbeat = None
        self.heartbeat_task = None
        self.delete_task = None

    async def setup_hook(self):

        # ======================
        # INIT DATABASE, load, sync (ASYNCMY)
        # ======================
        await init_database()
        await load_cogs(self)
        await sync_commands(self)

        # ======================
        # PERSISTENT VIEWS
        # ======================
        self.add_view(IntroPanel())
        self.add_view(FeedbackButton())

        self.add_view(ExecutiveInfoView("executive_guild"))
        self.add_view(ExecutiveInfoView("executive_sinyalid"))

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
            
    # =====================
    # async close
    # ====================
    async def close(self):

        if self.delete_task:
            self.delete_task.cancel()

            try:
                await self.delete_task
            except asyncio.CancelledError:
                pass

            self.delete_task = None

        if self.heartbeat_task:
            self.heartbeat_task.cancel()

            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass

            self.heartbeat_task = None

        if self.heartbeat:
            await self.heartbeat.close()
            self.heartbeat = None

        await close_database()

        await super().close()


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
    
    # ======================
    # REGISTER BOT
    # ======================
    await sync_bot_guilds(bot)
    
    # ======================
    # REMOVE UNAUTHORIZED GUILDS
    # ======================
    for guild in bot.guilds:

        if not await is_main_guild(guild.id):
            print(
                f"[Guild Access] Leaving unauthorized guild: "
                f"{guild.name} ({guild.id})"
            )

            await guild.leave()
            continue

        # ======================
        # SYNC MEMBERS
        # ======================
        await sync_guild_members(guild)

    print(
        f"[User Sync] Synced members from "
        f"{len(bot.guilds)} guild(s)"
    )
    
    # ======================
    # LOAD EMOJIS
    # ======================
    await load_emojis()

    # ======================
    # PRELOAD ROLE CACHE
    # ======================
    for guild in bot.guilds:

        if not await is_main_guild(guild.id):
            continue

        await load_roles(guild.id)

    print(f"Bot login sebagai {bot.user}")

    # ======================
    # DELETE CHECKER
    # ======================
    if (
        bot.delete_task is None
        or bot.delete_task.done()
    ):
        bot.delete_task = asyncio.create_task(
            delete_checker(bot)
        )

    # ======================
    # HEARTBEAT
    # ======================
    if (
        bot.heartbeat_task is None
        or bot.heartbeat_task.done()
    ):
        bot.heartbeat = HeartbeatTask(
            url=HEARTBEAT_CHECK,
            interval=30
        )

        bot.heartbeat_task = asyncio.create_task(
            bot.heartbeat.start()
        )

# ======================
# GUILD EVENTS
# ======================
@bot.event
async def on_guild_join(guild):
    if not await is_main_guild(guild.id):
        print(
            f"[Guild Access] Leaving unauthorized guild: "
            f"{guild.name} ({guild.id})"
        )
        await guild.leave()
        return
    await handle_guild_join(bot, guild)
    await sync_guild_members(guild)

@bot.event
async def on_guild_remove(guild):
    await handle_guild_remove(bot, guild)

# ======================
# MEMBER EVENTS
# ======================
@bot.event
async def on_member_join(member):

    if member.bot:
        return
    
    print(f"[JOIN] {member} joined {member.guild.name} ({member.guild.id})")

    await handle_member_join(member)


@bot.event
async def on_member_remove(member):

    if member.bot:
        return
    
    print(f"[LEFT] {member} left {member.guild.name} ({member.guild.id})")

    if await is_main_guild(member.guild.id):
        await handle_member_main_remove(member)

    await handle_member_remove_database(member)


@bot.event
async def on_member_update(before, after):

    if after.bot:
        return

    # Hanya proses guild yang termasuk guild_key "MAIN"
    main_guilds = await get_guild_ids("MAIN")

    if after.guild.id not in main_guilds:
        return

    if before.roles == after.roles:
        return

    role_groups = await get_roles(after.guild.id)

    # =========================
    # WELCOME CHECK
    # =========================
    if has_pangkat(after, role_groups):

        if has_role_group_change(
            before,
            after,
            role_groups
        ):
            await process_welcome(after)

    # =========================
    # EXECUTIVE NICKNAME CHECK
    # =========================
    await handle_executive_nickname(
        before,
        after
    )

# ======================
# ERROR HANDLER (!)
# ======================
@bot.event
async def on_command_error(
    ctx: commands.Context,
    error: commands.CommandError
):

    if isinstance(error, commands.CommandNotFound):
        return

    raise error

# ======================
# DISCORD GATEWAY LOG FILTER
# ======================
if is_production():

    class IgnoreGatewayResume(logging.Filter):

        def filter(self, record: logging.LogRecord) -> bool:
            return "has successfully RESUMED session" not in record.getMessage()


    logging.getLogger("discord.gateway").addFilter(
        IgnoreGatewayResume()
    )

# ======================
# RUN BOT
# ======================
bot.run(TOKEN)
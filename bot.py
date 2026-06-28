import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

from core.loader import (
    load_public_cogs,
    load_main_cogs,
    load_partner_growtopia_cogs,
)

from utils.delete_scheduler import delete_checker

from views.intro import IntroButton, register_persistent_views
from views.feedback import FeedbackButton, ReplyView
from views.executive_info_view import ExecutiveInfoView

from views.Partnership.Growtopia.introduction import GTIntroductionView

from database.guild_key_manager import get_guild_ids, is_main_guild

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
from events.member_main_remove import handle_member_main_remove
from events.member_remove import handle_member_remove_database
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
        
        self.add_view(GTIntroductionView())

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
    
    print(f"[JOIN] {member} joined {member.guild.name} ({member.guild.id})")

    if not await is_main_guild(member.guild.id):
        return

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
import os, discord
from dotenv import load_dotenv
from discord.ext import commands

from utils.delete_scheduler import delete_checker

from views.intro import IntroButton, register_persistent_views
from views.feedback import FeedbackButton, ReplyView
from views.executive_info_view import ExecutiveInfoView

from database.emoji_manager import load_emojis
from database.feedback_manager import get_pending_feedbacks
from database.role_manager import (
    get_roles,
    load_roles,
    get_roles_by_group
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
GUILD_ID = int(os.getenv("GUILD_ID"))

# ======================
# DISCORD INTENTS
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
        # LOAD ALL COGS RECURSIVE
        # ======================
        for root, dirs, files in os.walk("./cogs"):
            for filename in files:
                
                # hanya file python
                if not filename.endswith(".py"):
                    continue
                
                # skip private/helper files
                if filename.startswith("_"):
                    continue
                
                path = os.path.join(
                    root, 
                    filename
                )
                
                module = os.path.relpath(path, ".") \
                    .replace("\\", ".") \
                    .replace("/", ".") \
                    .removesuffix(".py")
                # hapus titik di depan jika ada
                # module = module.lstrip(".")
                
                await self.load_extension(
                    module
                )
                
        # ======================
        # REGISTER PERSISTENT VIEWS
        # ======================
        self.add_view(IntroButton())
        self.add_view(FeedbackButton())
                
        self.add_view(ExecutiveInfoView("guild"))
        self.add_view(ExecutiveInfoView("clan"))
        self.add_view(ExecutiveInfoView("sinyalid"))
        
        await register_persistent_views(self)
        
        # ======================
        # RESTORE FEEDBACK BUTTONS
        # ======================
        pending_feedbacks = get_pending_feedbacks()

        for feedback in pending_feedbacks:

            self.add_view(
                ReplyView(),
                message_id=feedback["message_id"]
            )
            
        # ======================
        # SYNC SLASH COMMANDS (GUILD-SPECIFIC)
        # ======================
        guild = discord.Object(
            id=GUILD_ID
        )
        
        self.tree.copy_global_to(
            guild=guild
        )
        
        synced = await self.tree.sync(
            guild=guild
        )
        
        print(
            f"Synced {len(synced)} commands (guild)"
        )

# ======================
# BOT INSTANCE
# ======================
bot = MyBot(
    command_prefix="!",
    intents=intents
)

# ======================
# BOT READY
# ======================
@bot.event
async def on_ready():
    load_emojis()
    bot.loop.create_task(delete_checker(bot))
    
    # preload semua guild roles ke cache
    for guild in bot.guilds:
        load_roles(guild.id)
    
    print(f"Bot login sebagai {bot.user}")

@bot.event
async def on_guild_join(guild):
    await handle_guild_join(guild)
    
@bot.event
async def on_guild_remove(guild):
    await handle_guild_remove(guild)

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

    # ❌ BUG 1: terlalu cepat return
    if before.roles == after.roles:
        return

    role_groups = get_roles(after.guild.id)
    changed_roles = get_changed_roles(before, after)

    # =========================
    # VERIFY CHECK
    # =========================
    verified_roles = set(role_groups["by_group"]["verified"].values())

    if changed_roles & verified_roles:
        await handle_verified(after)

    # =========================
    # WELCOME CHECK
    # =========================

    if has_pangkat(after, role_groups):

        # ❌ BUG 4: logic ini sering False karena timing Discord event
        if has_role_group_change(before, after, role_groups):
            await process_welcome(after)

bot.run(TOKEN)

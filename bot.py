import os, discord
from dotenv import load_dotenv
from discord.ext import commands
from utils.json_manager import FEEDBACK_PATH, load_json
from views.intro import (
    IntroButton,
    register_persistent_views
)
from utils.delete_scheduler import (
    delete_checker
)
from views.feedback import (
    FeedbackButton,
    ReplyView,
)
from views.executive_info_view import (
    ExecutiveInfoView,
)
from events.member_remove import (
    handle_member_remove
)
from events.member_join import (
    handle_member_join
)
from events.member_role_update import (
    get_changed_roles,
    get_role_groups,
    has_pangkat,
    has_role_group_change,
    process_welcome
)
from events.member_verified import (
    handle_verified
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
        self.add_view(
            IntroButton()
        )
        self.add_view(
            FeedbackButton()
        )
        self.add_view(
            ExecutiveInfoView("guild")
        )

        self.add_view(
            ExecutiveInfoView("clan")
        )

        self.add_view(
            ExecutiveInfoView("sinyalid")
        )
        # await restore_executive_info_timers(self)
        
        await register_persistent_views(
            self
        )
        
        # ======================
        # RESTORE FEEDBACK BUTTONS
        # ======================
        feedbacks = await load_json(FEEDBACK_PATH) or {}
        
        for guild_id, messages in feedbacks.items():
            for message_id, feedback_data in messages.items():
                
                # skip jika sudah dibalas
                if feedback_data["admin"]["reply"] is not None:
                    continue
                
                self.add_view(
                    ReplyView(),
                    message_id=int(message_id)
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
    bot.loop.create_task(
        delete_checker(bot)
    )
    print(f"Bot login sebagai {bot.user}")

@bot.event
async def on_member_join(member):
    await handle_member_join(member)
    
@bot.event
async def on_member_remove(member):
    await handle_member_remove(member)
    
@bot.event
async def on_member_update(before, after):

    if before.roles == after.roles:
        return

    role_groups = await get_role_groups(after.guild.id)

    changed_roles = get_changed_roles(before, after)

    # =========================
    # VERIFY CHECK (ONLY STEP 2)
    # =========================
    verified_roles = set(role_groups.get("verified", {}).values())

    if changed_roles & verified_roles:
        await handle_verified(after)

    # =========================
    # WELCOME CHECK (STEP 1 + 2)
    # =========================
    if has_pangkat(after, role_groups):

        if has_role_group_change(before, after, role_groups):
            await process_welcome(after)

bot.run(TOKEN)

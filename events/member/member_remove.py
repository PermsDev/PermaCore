import discord

from discord.ext import commands

from database.core.emoji_manager import get_emoji

from events.member.handlers.member_remove_intro import handle_member_remove_intro
from events.member.handlers.member_remove_welcome import handle_member_remove_welcome

from utils.logger import send_log

# ======================
# MEMBER REMOVE COG
# ======================

class MemberRemove(commands.Cog):

    def __init__(
        self,
        bot: commands.Bot
    ):

        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(
        self,
        member: discord.Member
    ):

        if member.bot:
            return

        print(
            f"[LEFT] {member} left "
            f"{member.guild.name} ({member.guild.id})"
        )

        # HANDLE MEMBER REMOVE

        await handle_member_remove_intro(member)
        await handle_member_remove_welcome(member)

        await send_log(
            guild=member.guild,
            log_type="INFORMATION",
            action="Member Remove",
            emoji=get_emoji("statusOffline"),
            user=member
        )


# ======================
# SETUP COG
# ======================

async def setup(
    bot: commands.Bot
):

    await bot.add_cog(
        MemberRemove(bot)
    )

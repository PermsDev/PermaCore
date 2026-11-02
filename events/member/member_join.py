import discord

from discord.ext import commands

from database.core.emoji_manager import get_emoji
from events.member.handlers.member_join_message import handle_member_join_unverified
from events.member.handlers.member_join_user_guild import handle_member_join_user_guild
from utils.logger import send_log


class MemberJoin(commands.Cog):

    def __init__(
        self,
        bot: commands.Bot
    ):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(
        self,
        member: discord.Member
    ):
        if member.bot:
            return

        print(
            f"[JOIN] {member} joined "
            f"{member.guild.name} ({member.guild.id})"
        )
        
        await handle_member_join_user_guild(member)
        await handle_member_join_unverified(member)
        
        # ======================
        # LOG
        # ======================
        await send_log(
            guild=member.guild,
            log_type="INFORMATION",
            action="Member Join",
            emoji=get_emoji("statusOnline"),
            user=member
        )


async def setup(
    bot: commands.Bot
):
    await bot.add_cog(
        MemberJoin(bot)
    )
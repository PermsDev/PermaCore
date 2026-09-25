from discord.ext import commands

from commands.sync.league import sync_league
from database.core.emoji_manager import reload_emojis


class Sync(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="sync",
        invoke_without_command=True
    )
    async def sync(
        self,
        ctx: commands.Context
    ):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                "Gunakan `!sync league` atau `!sync emoji`."
            )

    @sync.command(name="league")
    async def sync_league_command(
        self,
        ctx: commands.Context
    ):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send(
                "Tidak ada permission!"
            )
            return

        await sync_league(
            bot=self.bot,
            ctx=ctx
        )

    @sync.command(name="emoji")
    @commands.is_owner()
    async def sync_emoji(
        self,
        ctx: commands.Context
    ):
        msg = await ctx.send(
            "🔄 Sedang memuat ulang cache emoji dari database..."
        )

        try:
            await reload_emojis()

            await msg.edit(
                content="✅ Cache emoji berhasil diperbarui tanpa restart bot!"
            )

        except Exception as e:
            await msg.edit(
                content=f"❌ Gagal memuat cache: `{e}`"
            )


async def setup(bot):
    await bot.add_cog(Sync(bot))
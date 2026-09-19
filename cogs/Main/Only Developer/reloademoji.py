import discord
from discord.ext import commands

from database.core.emoji_manager import reload_emojis


class SyncCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="sync", invoke_without_command=True)
    @commands.is_owner()
    async def sync(self, ctx):
        await ctx.send("Gunakan: `!sync emoji`")

    @sync.command(name="emoji")
    @commands.is_owner()
    async def sync_emoji(self, ctx):

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
                content=f"❌ Gagal memuat ulang cache: `{e}`"
            )


async def setup(bot):
    await bot.add_cog(SyncCog(bot))
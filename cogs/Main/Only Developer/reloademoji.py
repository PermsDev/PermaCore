import discord
from discord.ext import commands
from database.emoji_manager import reload_emojis 

# 1. Buat class Cog-nya
class ReloadEmojiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 2. Masukkan perintahnya ke dalam class (perhatikan tambahan parameter 'self')
    @commands.command(name="reloademoji")
    @commands.is_owner()
    async def reload_emoji_cmd(self, ctx):
        msg = await ctx.send("🔄 Sedang memuat ulang cache emoji dari database...")
        try:
            await reload_emojis()
            await msg.edit(content="✅ Cache emoji berhasil diperbarui tanpa restart bot!")
        except Exception as e:
            await msg.edit(content=f"❌ Gagal memuat ulang cache: `{e}`")
            
# 3. Fungsi setup wajib untuk mendaftarkan class Cog di atas ke bot utama
async def setup(bot):
    await bot.add_cog(ReloadEmojiCog(bot))
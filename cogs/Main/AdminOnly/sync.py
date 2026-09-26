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
                "Gunakan `!sync league` atau `!sync emoji`.",
                delete_after=5
            )

    @sync.command(name="league")
    async def sync_league_command(
        self,
        ctx: commands.Context
    ):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send(
                "Tidak ada permission!",
                delete_after=5
            )
            return

        try:
            await sync_league(
                bot=self.bot,
                ctx=ctx
            )

        except Exception as e:
            print(
                f"[Sync League] Error: {e}"
            )

            await ctx.send(
                "Gagal melakukan sync League.",
                delete_after=5
            )

    @sync.command(name="emoji")
    @commands.is_owner()
    async def sync_emoji(
        self,
        ctx: commands.Context
    ):
        msg = await ctx.send(
            "🔄 Sedang memuat ulang cache emoji..."
        )

        try:
            await reload_emojis()

            await msg.edit(
                content="✅ Cache emoji berhasil diperbarui!"
            )

            await msg.delete(delay=5)

        except Exception as e:
            print(
                f"[Sync Emoji] Error: {e}"
            )

            await msg.edit(
                content="❌ Gagal memuat cache emoji."
            )

            await msg.delete(delay=5)

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx: commands.Context,
        error: commands.CommandError
    ):
        if ctx.command is None:
            return

        if isinstance(
            error,
            commands.CommandNotFound
        ):
            return

        if isinstance(
            error,
            commands.NotOwner
        ):
            await ctx.send(
                "Kamu tidak memiliki permission untuk command ini.",
                delete_after=5
            )
            return

        if isinstance(
            error,
            commands.MissingPermissions
        ):
            await ctx.send(
                "Kamu tidak memiliki permission untuk command ini.",
                delete_after=5
            )
            return

        if isinstance(
            error,
            commands.MissingRequiredArgument
        ):
            await ctx.send(
                "Argumen command tidak lengkap.",
                delete_after=5
            )
            return

        if isinstance(
            error,
            commands.BadArgument
        ):
            await ctx.send(
                "Argumen command tidak valid.",
                delete_after=5
            )
            return

        print(
            f"[Command Error] "
            f"{ctx.command.qualified_name}: {error}"
        )

        await ctx.send(
            "Terjadi error saat menjalankan command.",
            delete_after=5
        )


async def setup(bot):
    await bot.add_cog(Sync(bot))
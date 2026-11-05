
import discord

from discord.ext import commands

from database.core.channel_manager import get_channel, set_channel
from views.guild.league.embed.panel import create_top_score_panel
from config.constants import CLASH_CHANNEL_KEY


async def sync_league(
    bot,
    ctx: commands.Context
):

    guild_id = ctx.guild.id

    channel_data = await get_channel(
        guild_id=guild_id,
        channel_key=CLASH_CHANNEL_KEY
    )

    if channel_data is None:
        await ctx.send(
            "Channel League belum diset."
        )
        return

    channel_id = channel_data["channel_id"]
    old_message_id = channel_data["panel_message"]

    channel = bot.get_channel(channel_id)

    if channel is None:

        try:
            channel = await bot.fetch_channel(channel_id)

        except discord.NotFound:
            await ctx.send(
                "Channel League tidak ditemukan."
            )
            return

        except discord.HTTPException:
            await ctx.send(
                "Gagal mengambil channel League."
            )
            return

    if not isinstance(channel, discord.TextChannel):
        await ctx.send(
            "Channel League bukan Text Channel."
        )
        return

    if old_message_id:

        try:
            old_message = await channel.fetch_message(
                int(old_message_id)
            )

            await old_message.delete()

        except discord.NotFound:
            pass

        except discord.HTTPException:
            await ctx.send(
                "Gagal menghapus panel League lama."
            )
            return

    try:

        components = await create_top_score_panel()

        new_message = await channel.send(
            view=components
        )

    except discord.HTTPException as e:

        await ctx.send(
            f"Gagal membuat panel League:\n```{e}```"
        )
        return

    await set_channel(
        guild_id=guild_id,
        channel_key=CLASH_CHANNEL_KEY,
        channel_id=channel.id,
        panel_message=new_message.id
    )

    message = await ctx.send(
        f"Panel League berhasil disync di {channel.mention}."
    )

    await message.delete(delay=5)

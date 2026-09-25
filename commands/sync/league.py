import os

import aiohttp
import discord

from discord.ext import commands

from database.core.channel_manager import get_channel, set_channel
from views.guild.league.embed.panel import create_top_score_panel


async def sync_league(
    bot,
    ctx: commands.Context
):
    guild_id = ctx.guild.id

    channel_data = await get_channel(
        guild_id=guild_id,
        channel_key="clash_channel"
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

    components = await create_top_score_panel()

    token = os.getenv("TOKEN")

    url = (
        f"https://discord.com/api/v10/"
        f"channels/{channel.id}/messages"
    )

    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "flags": 32768,
        "components": [
            {
                "type": 17,
                "accent_color": 15844367,
                "spoiler": False,
                "components": components
            }
        ]
    }

    async with aiohttp.ClientSession() as session:

        async with session.post(
            url,
            headers=headers,
            json=payload
        ) as response:

            if response.status not in (200, 201):
                error = await response.text()

                await ctx.send(
                    f"Gagal membuat panel:\n```{error}```"
                )
                return

            data = await response.json()

    new_message_id = int(data["id"])

    await set_channel(
        guild_id=guild_id,
        channel_key="clash_channel",
        channel_id=channel.id,
        panel_message=new_message_id
    )

    await ctx.send(
        f"Panel League berhasil disync di {channel.mention}."
    )
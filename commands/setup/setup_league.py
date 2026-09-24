import os

import aiohttp
import discord

from views.league.embed.panel import create_top_score_panel


async def setup_league(
    bot,
    interaction: discord.Interaction,
    channel: discord.TextChannel
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "Tidak ada permission!",
            ephemeral=True
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

                await interaction.response.send_message(
                    f"Gagal membuat panel:\n```{error}```",
                    ephemeral=True
                )

                return

    await interaction.response.send_message(
        f"Panel League dibuat di {channel.mention}"
    )
import os

import aiohttp

from database.core.channel_manager import get_channel
from views.guild.league.embed.panel import create_top_score_panel


async def update_league_panel(
    guild_id: int
) -> bool:

    channel_data = await get_channel(
        guild_id=guild_id,
        channel_key="clash_channel"
    )

    if not channel_data:
        return False

    channel_id = channel_data.get("channel_id")
    message_id = channel_data.get("panel_message")

    if not channel_id or not message_id:
        return False

    token = os.getenv("TOKEN")

    if not token:
        return False

    components = await create_top_score_panel()

    url = (
        f"https://discord.com/api/v10/channels/"
        f"{channel_id}/messages/{message_id}"
    )

    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "components": components,
        "flags": 32768
    }

    async with aiohttp.ClientSession() as session:

        async with session.patch(
            url,
            headers=headers,
            json=payload
        ) as response:

            if response.status == 200:
                return True

            if response.status == 404:
                return False

            return False

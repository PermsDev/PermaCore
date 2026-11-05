import discord

from database.core.channel_manager import get_channel
from views.guild.league.embed.panel import create_top_score_panel
from config.constants import CLASH_CHANNEL_KEY


async def update_league_panel(
    bot: discord.Client,
    guild_id: int
) -> bool:

    channel_data = await get_channel(
        guild_id=guild_id,
        channel_key=CLASH_CHANNEL_KEY
    )

    if not channel_data:
        return False

    channel_id = channel_data.get("channel_id")
    message_id = channel_data.get("panel_message")

    if not channel_id or not message_id:
        return False

    try:
        channel = bot.get_channel(int(channel_id))

        if channel is None:
            channel = await bot.fetch_channel(int(channel_id))

        if not isinstance(channel, discord.TextChannel):
            return False

        message = await channel.fetch_message(
            int(message_id)
        )

        components = await create_top_score_panel()

        await message.edit(view=components)

        return True

    except discord.NotFound:
        return False

    except discord.Forbidden:
        print(
            f"[League] Tidak memiliki izin memperbarui panel "
            f"di channel {channel_id}."
        )
        return False

    except discord.HTTPException as e:
        print(f"[League] Gagal memperbarui panel: {e}")
        return False

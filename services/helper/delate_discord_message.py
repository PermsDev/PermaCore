import discord


async def delete_discord_message(
    guild: discord.Guild,
    channel_id: int,
    message_id: int,
    label: str
):
    channel = guild.get_channel(int(channel_id))

    if not channel:
        raise ValueError(
            f"Channel {channel_id} untuk {label} tidak ditemukan."
        )

    try:
        message = await channel.fetch_message(int(message_id))
        await message.delete()

    except discord.NotFound:
        raise

    except discord.Forbidden:
        raise

    except discord.HTTPException:
        raise
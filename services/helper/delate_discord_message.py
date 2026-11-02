import discord

# ======================
# DELETE DISCORD MESSAGE
# ======================

async def delete_discord_message(
    guild: discord.Guild,
    channel_id: int,
    message_id: int,
    label: str
):

    channel = guild.get_channel(
        int(channel_id)
    )

    if not channel:
        print(f"Channel {channel_id} untuk {label} tidak ditemukan.")
        return

    try:

        message = await channel.fetch_message(int(message_id))

        await message.delete()

        print(f"{label} berhasil dihapus.")

    except discord.NotFound:
        print(f"{label} tidak ditemukan.")

    except discord.Forbidden:
        print(f"Tidak ada izin menghapus {label}.")

    except discord.HTTPException as e:
        print(f"Gagal menghapus {label}: {e}")
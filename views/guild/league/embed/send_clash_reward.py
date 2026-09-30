import discord

from database.core.emoji_manager import get_emoji
from database.guild.door_password_manager import (
    get_door_password,
    get_door_password_shared_status
)
from utils.delete_scheduler import register_delete


async def send_clash_reward(
    user: discord.Member,
    guild_id: int,
    pass_id: int,
    growid: str,
    monthly_rank: int,
    monthly_points: int,
    total_rank: int,
    total_points: int
) -> bool:

    door = await get_door_password(
        guild_id=guild_id,
        pass_id=pass_id
    )

    if door is None:
        print(
            f"[Event Clash] Door password "
            f"{pass_id} tidak ditemukan."
        )
        return False

    if door["pass_door"] is None:
        print(
            f"[Event Clash] Password door "
            f"{pass_id} belum tersedia."
        )
        return False

    embed_info = discord.Embed(
        description=(
            f"## ❄️ Selamat Member {growid} ❄️\n"
            f"Kamu telah mencapai **Top #{monthly_rank}** "
            f"dalam Event Clash bulan ini.\n\n"
            f"Kamu telah memperoleh **{monthly_points} poin**.\n"
            f"Kamu berada di **peringkat #{total_rank}** "
            f"dengan total skor **{total_points} poin**."
        )
    )

    embed_reward = discord.Embed(
        title="🎁 Hadiah Tambahan",
        description=(
            "Silakan mengambil hadiah tambahan "
            "di world berikut:"
        )
    )

    embed_reward.add_field(
        name=f"{get_emoji('globe')}  Name World",
        value=f"`{door['world_name']}`",
        inline=False
    )

    embed_reward.add_field(
        name=f"{get_emoji('door_password')}  Name Door",
        value=f"`{door['name_door']}`",
        inline=False
    )

    embed_reward.add_field(
        name=f"{get_emoji('weak_password')}  Password Door",
        value=f"`{door['pass_door']}`",
        inline=False
    )

    try:

        message = await user.send(
            embeds=[
                embed_info,
                embed_reward
            ]
        )

    except discord.Forbidden:

        print(
            f"[Event Clash] DM tidak dapat dikirim "
            f"ke {user}."
        )
        return False

    except discord.HTTPException as error:

        print(
            f"[Event Clash] Gagal mengirim DM "
            f"ke {user}: {error}"
        )
        return False

    await register_delete(
        channel_id=message.channel.id,
        message_id=message.id,
        delete_after="1m"
    )

    await get_door_password_shared_status(
        guild_id=guild_id,
        pass_id=pass_id
    )

    return True
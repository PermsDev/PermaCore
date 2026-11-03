import discord

from services.helper.delate_discord_message import delete_discord_message

from database.core.intro_message_manager import (
    get_user_intro_messages,
    delete_user_intro_messages
)


async def handle_member_remove_intro(member: discord.Member):
    guild_id = member.guild.id
    user_id = member.id

    try:
        intro_messages = await get_user_intro_messages(
            guild_id=guild_id,
            user_id=user_id
        )

        for intro in intro_messages:
            await delete_discord_message(
                guild=member.guild,
                channel_id=intro["channel_id"],
                message_id=intro["message_id"],
                label=f"Introduction {intro['game_key']} untuk {member}"
            )

    except Exception as e:
        print(f"[MEMBER REMOVE] Gagal menghapus Introduction Discord {member}: {e}")

    try:
        await delete_user_intro_messages(
            guild_id=guild_id,
            user_id=user_id
        )

    except Exception as e:
        print(f"[MEMBER REMOVE] Gagal menghapus Introduction DB {member}: {e}")
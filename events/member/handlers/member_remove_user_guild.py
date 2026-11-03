import discord

from database.main.user.user_guild_manager import delete_user_guild


async def handle_member_remove_user_guild(
    member: discord.Member
):
    try:
        await delete_user_guild(
            user_id=member.id,
            guild_id=member.guild.id
        )

    except Exception as e:
        print(
            f"[MEMBER REMOVE] Gagal menghapus User Guild {member}: {e}"
        )
import discord

from database.main.user.user_guild_manager import delete_user_guild


async def handle_member_remove_user_guild(
    member: discord.Member
):
    try:
        deleted = await delete_user_guild(
            user_id=member.id,
            guild_id=member.guild.id
        )

        print(
            f"[MEMBER REMOVE] User Guild {member}: "
            f"{deleted} record berhasil dihapus."
        )

    except Exception as e:
        print(
            f"[MEMBER REMOVE] Gagal menghapus User Guild {member}: {e}"
        )
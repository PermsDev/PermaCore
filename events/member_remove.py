from database.intro_manager import (
    delete_all_user_intro,
    delete_user_profile
)

from database.guild_message_manager import (
    delete_guild_message
)


async def handle_member_remove_database(member):

    try:
        await delete_all_user_intro(member.guild.id, member.id)
        print(f"Intro DB {member} berhasil dihapus.")
    except Exception as e:
        print(f"Gagal hapus intro DB: {e}")

    try:
        await delete_guild_message(member.guild.id, member.id, "welcome")
        print(f"Welcome DB {member} berhasil dihapus.")
    except Exception as e:
        print(f"Gagal hapus welcome DB: {e}")

    try:
        await delete_user_profile(member.guild.id, member.id)
        print(f"User profile {member} berhasil dihapus.")
    except Exception as e:
        print(f"Gagal hapus user profile: {e}")
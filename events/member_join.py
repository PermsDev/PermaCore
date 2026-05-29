import discord

from utils.json_manager import (
    DM_MESSAGES_PATH,
    load_json,
    save_json
)
from utils.logger import send_log

async def handle_member_join(member: discord.Member):

    print(
        f"{member} baru masuk ke server "
        f"{member.guild.name}"
    )

    # ======================
    # LOAD DATA
    # ======================
    data = await load_json(
        DM_MESSAGES_PATH
    )

    guild_id = str(member.guild.id)
    user_id = str(member.id)

    # buat guild jika belum ada
    if guild_id not in data:
        data[guild_id] = {}

    # buat user jika belum ada
    if user_id not in data[guild_id]:
        data[guild_id][user_id] = {}

    # ======================
    # KIRIM DM
    # ======================
    try:
        # buka / ambil DM channel
        dm_channel = member.dm_channel

        if dm_channel is None:
            dm_channel = await member.create_dm()

        # hapus semua pesan lama di DM
        async for message in dm_channel.history(limit=None):
            try:
                await message.delete()
            except Exception as e:
                print(f"Gagal hapus DM {message.id}: {e}")
                
        # kirim pesan selamat datang
        dm_message = await member.send(
            f"## Selamat datang di server {member.guild.name}! <a:hi_man:1478080922883719238>\n"
            "Untuk Melanjutkan Progres Masuk Server, silahkan dapatkan 2 role verified dengan cara dibawah ini:\n\n"
            
            "### <a:statusOffline:1478032435164741777> Role 1: Verified Roles (1)\n"
            "- Kunjungi Channel <#1030430669597327380>\n"
            "- dan Click [Here](https://discord.com/channels/1030428036773990400/customize-community)\n"
            "- Klik reaction `Verified` Sampai mendapatkan role Verified 1\n\n"
            "### <a:statusOffline:1478032435164741777> Role 2: Verified Introduction (2)\n"
            "- Kunjungi Channel <#1501234394076020806>\n"
            "- Atau click [Here](https://discord.com/channels/1030428036773990400/1501234394076020806/1506363733608239275)\n"
            "- Isi formulir introduction untuk mendapatkan role Verified Introduction 2\n"
        )

        # simpan ID message DM
        data[guild_id][user_id]["welcome_dm_id"] = dm_message.id

        # save json
        await save_json(
            DM_MESSAGES_PATH,
            data
        )
        await send_log(
            guild=member.guild,
            log_type="INFORMATION",
            action="Member Join",
            emoji="<a:statusOnline:1478032492962250928>",
            user=member
        )

    except Exception as e:
        print(f"Gagal kirim DM: {e}")

    # ======================
    # KIRIM PESAN GENERAL
    # ======================
    channel = discord.utils.get(
        member.guild.text_channels,
        name="general"
    )

    if channel:
        await channel.send(
            f"Welcome {member.mention}!"
        )
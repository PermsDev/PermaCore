import discord
from database.core.emoji_manager import get_emoji

async def intro_embed() -> discord.Embed:
    
    emoji_intro = get_emoji("intro")

    return discord.Embed(
        description=(
            f"## {emoji_intro} Perkenalan Diri\n\n"

            "Selamat datang di panel **Perkenalan Diri**!\n"
            "Gunakan panel ini untuk mengatur informasi profile "
            "dan nama yang ditampilkan di server.\n\n"

            "👤 **Profile**\n"
            "Tambahkan nama panggilan serta akun game yang kamu "
            "miliki melalui tombol **Profile**.\n\n"

            "🏷️ **Display Name**\n"
            "Pilih informasi yang ingin digunakan sebagai "
            "display name server melalui tombol **Display Name**.\n\n"

            "━━━━━━━━━━━━━━━━━━━━\n"
            "-# **Tips:** Pastikan data yang kamu masukkan "
            "sudah benar sebelum menyimpannya."
        ),
        color=discord.Color.green()
    )
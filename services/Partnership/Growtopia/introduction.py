import discord
import traceback

from database.channel_manager import set_channel
from views.Partnership.Growtopia.introduction import GTIntroductionView

CHANNEL_KEY = "GT_INTRO"


async def gt_setup_introduction(
    interaction: discord.Interaction,
    channel: discord.TextChannel
):

    await set_channel(
        guild_id=interaction.guild.id,
        channel_key=CHANNEL_KEY,
        channel_id=channel.id,
        panel_message=None
    )

    embed = discord.Embed(
        title="🌱 Growtopia Introduction",
        description=(
            "Silakan tekan tombol di bawah untuk mengisi "
            "form introduction."
        ),
        color=discord.Color.green()
    )

    try:
        panel = await channel.send(
            embed=embed,
            view=GTIntroductionView()
        )

    except discord.Forbidden:
        print("\n========== Forbidden ==========")
        print(f"Guild   : {interaction.guild.id}")
        print(f"Channel : {channel.id}")
        print(f"Bot     : {interaction.guild.me}")
        print("================================\n")

        return await interaction.response.send_message(
            "❌ Saya tidak memiliki akses untuk mengirim pesan ke channel tersebut.",
            ephemeral=True
        )

    except Exception:
        print("\n========== SEND PANEL ERROR ==========")
        traceback.print_exc()
        print("======================================\n")

        return await interaction.response.send_message(
            "❌ Terjadi error saat mengirim panel. Cek console.",
            ephemeral=True
        )

    try:
        await set_channel(
            guild_id=interaction.guild.id,
            channel_key=CHANNEL_KEY,
            channel_id=channel.id,
            panel_message=panel.id
        )

    except Exception:
        print("\n========== SAVE PANEL MESSAGE ERROR ==========")
        traceback.print_exc()
        print("==============================================\n")

        return await interaction.response.send_message(
            "❌ Panel berhasil dikirim tetapi gagal menyimpan message_id ke database.",
            ephemeral=True
        )

    await interaction.response.send_message(
        f"✅ Panel berhasil dikirim ke {channel.mention}.",
        ephemeral=True
    )
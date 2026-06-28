import discord
import traceback

from database.channel_manager import (
    get_channel,
    set_channel
)
from database.role_manager import (
    set_role,
    delete_role
)

from views.Partnership.Growtopia.introduction import GTIntroductionView

CHANNEL_KEY = "GT_INTRO"

ROLE_GROUP = "PartnerGT"
ROLE_KEY = "introduction"


async def gt_setup_introduction(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    roles: discord.Role | None = None
):

    # ==================================================
    # HAPUS PANEL LAMA
    # ==================================================

    try:

        old_channel = await get_channel(
            interaction.guild.id,
            CHANNEL_KEY
        )

        if old_channel:

            old_channel_obj = interaction.guild.get_channel(
                old_channel["channel_id"]
            )

            if (
                old_channel_obj is not None
                and old_channel["panel_message"]
            ):

                try:
                    old_message = await old_channel_obj.fetch_message(
                        old_channel["panel_message"]
                    )

                    await old_message.delete()

                except discord.NotFound:
                    pass

                except discord.Forbidden:
                    pass

    except Exception:
        print("\n========== DELETE OLD PANEL ERROR ==========")
        traceback.print_exc()
        print("============================================\n")

    # ==================================================
    # EMBED
    # ==================================================

    embed = discord.Embed(
        title="🌱 Growtopia Introduction",
        description=(
            "Silakan tekan tombol di bawah "
            "untuk mengisi form introduction."
        ),
        color=discord.Color.green()
    )

    # ==================================================
    # KIRIM PANEL
    # ==================================================

    try:

        panel = await channel.send(
            embed=embed,
            view=GTIntroductionView()
        )

    except discord.Forbidden:

        print("\n========== Forbidden ==========")
        print(f"Guild   : {interaction.guild.id}")
        print(f"Channel : {channel.id}")
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
            "❌ Terjadi error saat mengirim panel.",
            ephemeral=True
        )

    # ==================================================
    # SIMPAN CHANNEL
    # ==================================================

    try:

        await set_channel(
            guild_id=interaction.guild.id,
            channel_key=CHANNEL_KEY,
            channel_id=channel.id,
            panel_message=panel.id
        )

    except Exception:

        print("\n========== SAVE CHANNEL ERROR ==========")
        traceback.print_exc()
        print("========================================\n")

        try:
            await panel.delete()
        except Exception:
            pass

        return await interaction.response.send_message(
            "❌ Panel berhasil dikirim tetapi gagal menyimpan konfigurasi.",
            ephemeral=True
        )

    # ==================================================
    # SIMPAN ROLE
    # ==================================================

    try:
        if roles is None:

            await delete_role(
                guild_id=interaction.guild.id,
                role_group=ROLE_GROUP,
                role_key=ROLE_KEY
            )

        else:

            await set_role(
                guild_id=interaction.guild.id,
                role_id=roles.id,
                role_group=ROLE_GROUP,
                role_key=ROLE_KEY
            )

    except Exception:

        print("\n========== SAVE ROLE ERROR ==========")
        traceback.print_exc()
        print("=====================================\n")

        return await interaction.response.send_message(
            "❌ Panel berhasil dibuat tetapi gagal menyimpan role.",
            ephemeral=True
        )

    # ==================================================
    # SUCCESS
    # ==================================================

    message = (
        f"✅ Panel berhasil dikirim ke {channel.mention}."
    )

    if roles:
        message += (
            f"\n🎖️ Role setelah introduction: {roles.mention}"
        )
    else:
        message += (
            "\n🎖️ Tidak ada role yang akan diberikan."
        )

    await interaction.response.send_message(
        message,
        ephemeral=True
    )
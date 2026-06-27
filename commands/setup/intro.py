import asyncio

import discord

from views.intro import IntroButton

from database.channel_manager import (
    get_channel,
    set_channel
)


async def setup_intro(
    bot,
    interaction: discord.Interaction,
    channel: discord.TextChannel
):
    """
    Setup intro panel.
    """

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            "Tidak ada permission!",
            ephemeral=True
        )
        return

    # =====================================
    # Hapus panel lama
    # =====================================

    old_data = await get_channel(
        interaction.guild.id,
        "INTRO_CHANNEL"
    )

    if old_data:

        old_msg_id = old_data["panel_message"]
        old_channel_id = old_data["channel_id"]

        try:

            old_channel = bot.get_channel(
                old_channel_id
            )

            if old_channel and old_msg_id:

                old_msg = await old_channel.fetch_message(
                    old_msg_id
                )

                await old_msg.delete()

        except discord.NotFound:
            pass

        except discord.Forbidden:
            pass

        except discord.HTTPException:
            pass

    # =====================================
    # Kirim panel baru
    # =====================================

    embed = discord.Embed(
        title="🪪 Daftar Member Perma Community",
        description=(
            "Klik tombol di bawah "
            "untuk mengisi form biodata kamu!"
        ),
        color=discord.Color.green()
    )

    view = IntroButton()

    msg = await channel.send(
        embed=embed,
        view=view
    )

    # =====================================
    # Simpan database
    # =====================================    
    await set_channel(
        interaction.guild.id,
        "INTRO_CHANNEL",
        channel.id,
        msg.id
    )

    # =====================================
    # Response
    # =====================================

    await interaction.response.send_message(
        f"Panel intro diperbarui di "
        f"{channel.mention}"
    )
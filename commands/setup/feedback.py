import asyncio

import discord

from views.feedback import FeedbackButton

from database.channel_manager import (
    get_channel,
    set_channel
)


async def setup_feedback(
    bot,
    interaction: discord.Interaction,
    panel_channel: discord.TextChannel,
    target_channel: discord.TextChannel
):
    """
    Setup feedback panel.
    """

    await interaction.response.defer(
        ephemeral=True
    )

    if not interaction.user.guild_permissions.administrator:

        await interaction.followup.send(
            "Tidak ada permission!",
            ephemeral=True
        )
        return

    # =====================================
    # Hapus panel lama
    # =====================================

    old_data = await get_channel(
        interaction.guild.id,
        "FEEDBACK_PANEL_CHANNEL"
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

        except Exception:
            pass

    # =====================================
    # Kirim panel baru
    # =====================================

    embed = discord.Embed(
        title="📨 Feedback Server",
        description=(
            "Pilih kategori feedback "
            "dari dropdown di bawah."
        ),
        color=discord.Color.blurple()
    )

    view = FeedbackButton()

    msg = await panel_channel.send(
        embed=embed,
        view=view
    )

    # =====================================
    # Simpan database
    # =====================================
    await set_channel(
        interaction.guild.id,
        "FEEDBACK_PANEL_CHANNEL",
        panel_channel.id,
        msg.id
    )
    
    await set_channel(
        interaction.guild.id,
        "FEEDBACK_TARGET_CHANNEL",
        target_channel.id
    )

    # =====================================
    # Response
    # =====================================

    await interaction.followup.send(
        f"Panel feedback dibuat di "
        f"{panel_channel.mention}",
        ephemeral=True
    )
import discord

from database.channel_manager import (
    set_channel
)


async def setup_welcome(
    interaction: discord.Interaction,
    channel: discord.TextChannel
):
    """
    Setup welcome channel.
    """

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            "Tidak ada permission!",
            ephemeral=True
        )
        return

    # =====================================
    # SIMPAN DATABASE
    # =====================================
    await set_channel(
        interaction.guild.id,
        "WELCOME_CHANNEL",
        channel.id
    )

    # =====================================
    # RESPONSE
    # =====================================

    embed = discord.Embed(
        title="✅ Welcome Channel Updated",
        description=(
            f"Welcome channel berhasil "
            f"diatur ke {channel.mention}"
        ),
        color=discord.Color.green()
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )
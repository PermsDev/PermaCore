import discord

from database.core.channel_manager import (
    get_channel,
    set_channel
)

from views.guild.guild_panel import create_guild_manage_panel
from views.guild.guild_view import GuildManageView


GUILD_MANAGE_CHANNEL_KEY = "guild_manage_channel"

async def setup_guildManage(
    interaction: discord.Interaction,
    channel: discord.TextChannel
):
    # ==================================================
    # CHECK PERMISSION
    # ==================================================
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "Tidak ada permission!",
            ephemeral=True
        )
        return

    guild_id = interaction.guild.id

    # ==================================================
    # AMBIL PANEL LAMA
    # ==================================================
    old_panel = await get_channel(
        guild_id,
        GUILD_MANAGE_CHANNEL_KEY
    )

    # ==================================================
    # HAPUS PANEL LAMA
    # ==================================================
    if old_panel:
        old_channel_id = old_panel["channel_id"]
        old_message_id = old_panel["panel_message"]

        if old_channel_id and old_message_id:
            old_channel = interaction.guild.get_channel(
                int(old_channel_id)
            )

            if old_channel is not None:
                try:
                    old_message = await old_channel.fetch_message(
                        int(old_message_id)
                    )

                    await old_message.delete()

                except discord.NotFound:
                    # Message sudah tidak ada
                    pass

                except discord.Forbidden:
                    # Bot tidak punya permission
                    pass

                except discord.HTTPException:
                    # Error dari Discord API
                    pass

    # ==================================================
    # BUAT PANEL BARU
    # ==================================================
    message = await channel.send(
        embed=create_guild_manage_panel(),
        view=GuildManageView()
    )

    # ==================================================
    # SIMPAN PANEL BARU
    # ==================================================
    await set_channel(
        guild_id=guild_id,
        channel_key=GUILD_MANAGE_CHANNEL_KEY,
        channel_id=channel.id,
        panel_message=message.id
    )

    # ==================================================
    # RESPONSE
    # ==================================================
    await interaction.response.send_message(
        f"Panel Guild Management dibuat di {channel.mention}"
    )

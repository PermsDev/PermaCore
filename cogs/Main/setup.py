import discord
from discord import app_commands
from discord.ext import commands

from views.intro import IntroButton
from views.feedback import FeedbackButton

from database.channel_manager import (
    get_channel,
    set_channel
)

# ======================
# COG
# ======================
class Setup(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    setup = app_commands.Group(
        name="setup",
        description="Setup server",
        default_permissions=discord.Permissions(
            administrator=True
        )
    )

    # ======================
    # SETUP INTRO
    # ======================
    @setup.command(
        name="intro",
        description="Set channel intro | Admin only"
    )
    async def setup_intro(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):

        if not interaction.user.guild_permissions.administrator:

            await interaction.response.send_message(
                "Tidak ada permission!",
                ephemeral=True
            )
            return

        # =========================
        # HAPUS PANEL LAMA
        # =========================
        old_data = get_channel(
            interaction.guild.id,
            "INTRO_CHANNEL"
        )

        if old_data:

            old_msg_id = old_data["panel_message"]
            old_channel_id = old_data["channel_id"]

            try:

                old_channel = self.bot.get_channel(
                    old_channel_id
                )

                if old_channel and old_msg_id:

                    old_msg = await old_channel.fetch_message(
                        old_msg_id
                    )

                    await old_msg.delete()

            except:
                pass

        # =========================
        # KIRIM PANEL BARU
        # =========================
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

        # =========================
        # SIMPAN DATABASE
        # =========================
        set_channel(
            interaction.guild.id,
            "INTRO_CHANNEL",
            channel.id,
            msg.id
        )

        await interaction.response.send_message(
            f"Panel intro diperbarui di "
            f"{channel.mention}"
        )

    # ======================
    # SETUP FEEDBACK
    # ======================
    @setup.command(
        name="feedback",
        description="Setup feedback panel | Admin only"
    )
    async def setup_feedback(
        self,
        interaction: discord.Interaction,
        panel_channel: discord.TextChannel,
        target_channel: discord.TextChannel
    ):

        await interaction.response.defer(
            ephemeral=True
        )

        if not interaction.user.guild_permissions.administrator:

            await interaction.followup.send(
                "Tidak ada permission!",
                ephemeral=True
            )
            return

        # =========================
        # HAPUS PANEL LAMA
        # =========================
        old_data = get_channel(
            interaction.guild.id,
            "FEEDBACK_PANEL_CHANNEL"
        )

        if old_data:

            old_msg_id = old_data["panel_message"]
            old_channel_id = old_data["channel_id"]

            try:

                old_channel = self.bot.get_channel(
                    old_channel_id
                )

                if old_channel and old_msg_id:

                    old_msg = await old_channel.fetch_message(
                        old_msg_id
                    )

                    await old_msg.delete()

            except:
                pass

        # =========================
        # KIRIM PANEL BARU
        # =========================
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

        # =========================
        # SIMPAN DATABASE
        # =========================
        set_channel(
            interaction.guild.id,
            "FEEDBACK_PANEL_CHANNEL",
            panel_channel.id,
            msg.id
        )

        set_channel(
            interaction.guild.id,
            "FEEDBACK_TARGET_CHANNEL",
            target_channel.id
        )

        await interaction.followup.send(
            f"Panel feedback dibuat di "
            f"{panel_channel.mention}",
            ephemeral=True
        )

    # ======================
    # SETUP LOG
    # ======================
    @setup.command(
        name="log",
        description="Setup log channel | Admin only"
    )
    async def setup_log(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):

        if not interaction.user.guild_permissions.administrator:

            await interaction.response.send_message(
                "Tidak ada permission!",
                ephemeral=True
            )
            return

        set_channel(
            interaction.guild.id,
            "LOG_CHANNEL",
            channel.id
        )

        embed = discord.Embed(
            title="✅ Log Channel Updated",
            description=(
                f"Channel log berhasil "
                f"diatur ke {channel.mention}"
            ),
            color=discord.Color.orange()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ======================
    # SETUP WELCOME
    # ======================
    @setup.command(
        name="welcome",
        description="Setup welcome channel | Admin only"
    )
    async def setup_welcome(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):

        if not interaction.user.guild_permissions.administrator:

            await interaction.response.send_message(
                "Tidak ada permission!",
                ephemeral=True
            )
            return

        set_channel(
            interaction.guild.id,
            "WELCOME_CHANNEL",
            channel.id
        )

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


# ======================
# LOAD COG
# ======================
async def setup(bot):
    await bot.add_cog(Setup(bot))
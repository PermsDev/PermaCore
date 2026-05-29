import discord
from discord import app_commands
from discord.ext import commands

from views.intro import IntroButton
from views.feedback import FeedbackButton

from utils.json_manager import (
    GUILD_SETTINGS_PATH,
    load_json,
    update_json
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

        guild_id = str(interaction.guild.id)

        # =========================
        # LOAD DATA UNTUK DELETE
        # =========================
        data = await load_json(
            GUILD_SETTINGS_PATH
        )

        guild_data = data.get(guild_id, {})

        old_msg_id = guild_data.get(
            "intro_message_id"
        )

        old_channel_id = guild_data.get(
            "intro_channel_id"
        )

        # =========================
        # HAPUS PANEL LAMA
        # =========================
        if old_msg_id and old_channel_id:

            try:

                old_channel = self.bot.get_channel(
                    old_channel_id
                )

                if old_channel:

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
        # UPDATE JSON
        # =========================
        def updater(data):

            if guild_id not in data:
                data[guild_id] = {}

            data[guild_id]["intro_message_id"] = msg.id
            data[guild_id]["intro_channel_id"] = channel.id

        await update_json(
            GUILD_SETTINGS_PATH,
            updater
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

        guild_id = str(interaction.guild.id)

        # =========================
        # LOAD DATA UNTUK DELETE
        # =========================
        data = await load_json(
            GUILD_SETTINGS_PATH
        )

        guild_data = data.get(guild_id, {})

        old_msg_id = guild_data.get(
            "feedback_message_id"
        )

        old_channel_id = guild_data.get(
            "feedback_panel_channel"
        )

        # =========================
        # HAPUS PANEL LAMA
        # =========================
        if old_msg_id and old_channel_id:

            try:

                old_channel = self.bot.get_channel(
                    old_channel_id
                )

                if old_channel:

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
        # UPDATE JSON
        # =========================
        def updater(data):

            if guild_id not in data:
                data[guild_id] = {}

            data[guild_id][
                "feedback_panel_channel"
            ] = panel_channel.id

            data[guild_id][
                "feedback_target_channel"
            ] = target_channel.id

            data[guild_id][
                "feedback_message_id"
            ] = msg.id

        await update_json(
            GUILD_SETTINGS_PATH,
            updater
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

        guild_id = str(interaction.guild.id)

        # =========================
        # UPDATE JSON
        # =========================
        def updater(data):

            if guild_id not in data:
                data[guild_id] = {}

            data[guild_id][
                "log_channel"
            ] = channel.id

        await update_json(
            GUILD_SETTINGS_PATH,
            updater
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

        guild_id = str(interaction.guild.id)

        # =========================
        # UPDATE JSON
        # =========================
        def updater(data):

            if guild_id not in data:
                data[guild_id] = {}

            data[guild_id][
                "welcome_channel_id"
            ] = channel.id

        await update_json(
            GUILD_SETTINGS_PATH,
            updater
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

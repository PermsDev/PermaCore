import discord
import asyncio

from datetime import datetime
from database.feedback_manager import (
    create_feedback,
    reply_feedback
)
from utils.delete_scheduler import register_delete
from utils.logger import send_log

from database.channel_manager import get_channel

lock = asyncio.Lock()
reply_lock = set()

# ======================
# BALASAN ADMIN
# ======================
class ReplyModal(discord.ui.Modal, title="Balas Feedback"):

    reply = discord.ui.TextInput(
        label="Balasan",
        style=discord.TextStyle.paragraph,
        placeholder="Tulis balasan...",
        required=True,
        max_length=1000
    )

    def __init__(
        self,
        user_id: int,
        original_embed: discord.Embed,
        message: discord.Message
    ):
        super().__init__()

        self.user_id = user_id
        self.original_embed = original_embed
        self.message = message

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        print("[FEEDBACK] Reply process started")

        await interaction.response.defer(ephemeral=True)

        message_id = self.message.id

        print(f"[FEEDBACK] Message ID: {message_id}")
        print(f"[FEEDBACK] Admin: {interaction.user} ({interaction.user.id})")

        if message_id in reply_lock:

            print("[FEEDBACK] Already being processed")

            await interaction.followup.send(
                "Feedback sedang diproses.",
                ephemeral=True
            )
            return

        reply_lock.add(message_id)

        print("[FEEDBACK] Lock acquired")

        try:

            print(f"[FEEDBACK] Fetching user {self.user_id}")

            user = await interaction.client.fetch_user(
                self.user_id
            )

            print(
                f"[FEEDBACK] User found: "
                f"{user} ({user.id})"
            )

            # ======================
            # DM USER
            # ======================
            print("[FEEDBACK] Building DM embed")

            dm_embed = discord.Embed(
                title="📨 Balasan Feedback",
                description=self.reply.value,
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )

            dm_embed.add_field(
                name="Admin",
                value=interaction.user.mention,
                inline=False
            )

            print("[FEEDBACK] Sending DM")

            dm_msg = await user.send(
                embed=dm_embed
            )

            print(
                f"[FEEDBACK] DM sent "
                f"(channel={dm_msg.channel.id}, "
                f"message={dm_msg.id})"
            )

            print("[FEEDBACK] Register delete scheduler")

            await register_delete(
                channel_id=dm_msg.channel.id,
                message_id=dm_msg.id,
                delete_after="7d"
            )

            print("[FEEDBACK] Delete scheduler registered")

            # ======================
            # EDIT FEEDBACK EMBED
            # ======================
            print("[FEEDBACK] Updating feedback embed")

            embed = self.original_embed.copy()

            embed.color = discord.Color.green()

            embed.add_field(
                name="Dibalas Oleh",
                value=interaction.user.mention,
                inline=False
            )

            embed.add_field(
                name="Balasan",
                value=self.reply.value,
                inline=False
            )

            embed.set_footer(
                text="Status: Sudah Dibalas"
            )

            await self.message.edit(
                embed=embed,
                view=None
            )

            print("[FEEDBACK] Feedback message updated")

            # ======================
            # SAVE DATA
            # ======================
            print("[FEEDBACK] Saving to database")

            await reply_feedback(
                message_id=message_id,
                admin_id=interaction.user.id,
                admin_name=str(interaction.user),
                reply=self.reply.value,
                replied_at=datetime.now()
            )

            print("[FEEDBACK] Database updated")

            # ======================
            # LOG
            # ======================
            print("[FEEDBACK] Sending log")

            await send_log(
                guild=interaction.guild,
                log_type="SUCCESS",
                action="Reply Feedback",
                emoji="✉️",
                user=interaction.user,
                details={
                    "Target User": f"<@{self.user_id}>",
                    "Link Message": f"[Klik Disini]({self.message.jump_url})"
                }
            )

            print("[FEEDBACK] Log sent")

            await interaction.followup.send(
                "Balasan berhasil dikirim.",
                ephemeral=True
            )

            print("[FEEDBACK] Reply completed successfully")

        except discord.Forbidden:

            print(
                f"[FEEDBACK] DM CLOSED "
                f"for user {self.user_id}"
            )

            await send_log(
                guild=interaction.guild,
                log_type="WARNING",
                emoji="⚠️",
                action="Reply Feedback",
                user=interaction.user,
                details={
                    "Target User": f"<@{self.user_id}>",
                    "Link Message": f"[Klik Disini]({self.message.jump_url})",
                    "Error": "DM user tertutup."
                }
            )

            await interaction.followup.send(
                "User menutup DM.",
                ephemeral=True
            )

        except Exception as e:

            print(
                f"[FEEDBACK] ERROR: "
                f"{type(e).__name__}: {e}"
            )

            await send_log(
                guild=interaction.guild,
                log_type="ERROR",
                emoji="❌",
                action="Reply Feedback",
                user=interaction.user,
                details={
                    "Target User": f"<@{self.user_id}>",
                    "Link Message": f"[Klik Disini]({self.message.jump_url})",
                    "Error": str(e)
                }
            )

            await interaction.followup.send(
                "Terjadi error saat mengirim balasan.",
                ephemeral=True
            )

        finally:

            reply_lock.discard(message_id)

            print(
                f"[FEEDBACK] Lock released "
                f"for message {message_id}"
            )

# ======================
# VIEW BALASAN ADMIN
# ======================
class ReplyView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Balas",
        emoji="✉️",
        style=discord.ButtonStyle.green,
        custom_id="feedback_reply_button"
    )
    async def reply_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not interaction.user.guild_permissions.manage_messages:

            await interaction.response.send_message(
                "Tidak ada permission.",
                ephemeral=True
            )
            return

        if not interaction.message.embeds:
            await interaction.response.send_message(
                "Embed tidak ditemukan.",
                ephemeral=True
            )
            return

        embed = interaction.message.embeds[0]

        if (
            embed.footer
            and embed.footer.text
            and "Sudah Dibalas" in embed.footer.text
        ):

            await interaction.response.send_message(
                "Feedback sudah dibalas.",
                ephemeral=True
            )
            return

        try:
            user_field = embed.fields[0].value
            user_id = int(user_field.split("`")[1])

        except Exception:

            await interaction.response.send_message(
                "Gagal membaca data user.",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            ReplyModal(
                user_id,
                embed.copy(),
                interaction.message
            )
        )

# ======================
# MODAL FEEDBACK
# ======================
class FeedbackModal(discord.ui.Modal, title="Kirim Feedback"):

    feedback = discord.ui.TextInput(
        label="Feedback",
        style=discord.TextStyle.paragraph,
        placeholder="Tulis feedback kamu...",
        required=True,
        max_length=1000
    )

    def __init__(self, category: str):

        super().__init__()

        self.category = category

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.defer(
            ephemeral=True
        )

        # ======================
        # AMBIL CHANNEL FEEDBACK
        # ======================
        channel_data = await get_channel(
            interaction.guild.id,
            "FEEDBACK_TARGET_CHANNEL"
        )

        if not channel_data:

            await interaction.followup.send(
                "Channel feedback belum disetting.",
                ephemeral=True
            )
            return

        channel_id = channel_data["channel_id"]

        channel = interaction.guild.get_channel(
            channel_id
        )

        if not channel:

            await interaction.followup.send(
                "Channel feedback tidak ditemukan.",
                ephemeral=True
            )
            return

        # ======================
        # EMBED
        # ======================
        embed = discord.Embed(
            title="📨 Feedback Baru",
            color=discord.Color.blurple(),
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(
            name="User",
            value=(
                f"{interaction.user.mention} "
                f"(`{interaction.user.id}`)"
            ),
            inline=False
        )

        embed.add_field(
            name="Kategori",
            value=self.category,
            inline=False
        )

        embed.add_field(
            name="Pesan",
            value=self.feedback.value,
            inline=False
        )

        embed.set_thumbnail(
            url=interaction.user.display_avatar.url
        )

        embed.set_footer(
            text="Status: Menunggu Balasan"
        )

        view = ReplyView()

        msg = await channel.send(
            embed=embed,
            view=view
        )

        # ======================
        # SAVE
        # ======================
        await create_feedback(
            message_id=msg.id,
            guild_id=interaction.guild.id,
            channel_id=channel.id,

            category=self.category,

            user_id=interaction.user.id,
            username=str(interaction.user),

            feedback=self.feedback.value,
            sent_at=datetime.now()
        )

        # ======================
        # LOG
        # ======================
        await send_log(
            guild=interaction.guild,
            log_type="SUCCESS",
            action="Feedback",
            emoji="📨",
            user=interaction.user,
            details={
                "Kategori": self.category,
                "Link Message": (
                    f"[Klik Disini]"
                    f"({msg.jump_url})"
                )
            }
        )

        await interaction.followup.send(
            "Feedback berhasil dikirim!",
            ephemeral=True
        )
# ======================
# DROPDOWN CATEGORY
# ======================
class FeedbackCategorySelect(discord.ui.Select):

    def __init__(self):

        options = [

            discord.SelectOption(
                label="Bot Discord",
                emoji="🤖"
            ),

            discord.SelectOption(
                label="Server Discord",
                emoji="💬"
            ),

            discord.SelectOption(
                label="Guild Growtopia",
                emoji="🌍"
            ),

            discord.SelectOption(
                label="Clan Pixel World",
                emoji="🎮"
            ),

            discord.SelectOption(
                label="Other",
                emoji="📦"
            )
        ]

        super().__init__(
            placeholder="Pilih kategori feedback...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="feedback_category_select"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        category = self.values[0]

        await interaction.response.send_modal(
            FeedbackModal(category)
        )

# ======================
# VIEW FEEDBACK
# ======================
class FeedbackButton(discord.ui.View):

    def __init__(self):

        super().__init__(timeout=None)

        self.add_item(
            FeedbackCategorySelect()
        )
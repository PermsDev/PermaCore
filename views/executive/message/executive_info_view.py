import discord

from utils.delete_scheduler import register_delete

from database.core.emoji_manager import get_emoji
from database.core.executive.executive_manager import (
    get_executive,
    get_executive_section
)


# =========================
# BUILD CONTENT EMBED
# =========================
def build_content_embed(data):

    if not data:
        return discord.Embed(
            title="Executive Information",
            description="Sedang dalam pembuatan.",
            color=discord.Color.blurple()
        )

    # =========================
    # DESCRIPTION
    # =========================
    description = data.get("description")

    if not description or str(description).strip() == "":
        description = "Sedang dalam pembuatan."

    # =========================
    # TITLE
    # =========================
    emoji = ""

    emoji_key = data.get("emoji_key")

    if emoji_key:
        emoji = get_emoji(emoji_key) or ""

    section_name = data.get("section_name", "Information")
    executive_name = data.get("executive_name", "Executive")

    title = f"{emoji} {section_name} {executive_name}".strip()

    # =========================
    # CREATE EMBED
    # =========================
    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.blurple()
    )

    return embed


# =========================
# DROPDOWN SELECT
# =========================
class ExecutiveInfoSelect(discord.ui.Select):

    def __init__(self, executive_type: str):

        # =========================
        # LOAD EXECUTIVE DATA
        # =========================
        self.executive_type = executive_type

        # =========================
        # OPTIONS
        # =========================
        options = [
            discord.SelectOption(
                label="Tugas Executive",
                value="tugas",
                emoji=get_emoji("gold_crown"),
                description="Lihat tugas executive"
            ),

            discord.SelectOption(
                label="Aturan Executive",
                value="aturan",
                emoji=get_emoji("gtScroll"),
                description="Lihat aturan executive"
            ),

            discord.SelectOption(
                label="Hak & Akses Executive",
                value="hak_akses",
                emoji=get_emoji("checklist"),
                description="Lihat hak dan akses executive"
            ),

            discord.SelectOption(
                label="Benefit Executive",
                value="benefit",
                emoji=get_emoji("bgl"),
                description="Lihat benefit executive"
            ),

            discord.SelectOption(
                label="Executive Promotion Guide",
                value="jenjang",
                emoji=get_emoji("hype"),
                description="Lihat promotion path"
            )
        ]

        super().__init__(
            placeholder="Pilih informasi executive",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"executive_info_select:{executive_type}"
        )

    # =========================
    # CALLBACK
    # =========================
    async def callback(self, interaction: discord.Interaction):

        selected = self.values[0]
        executive_type = self.executive_type

        # =========================
        # GET EXECUTIVE TYPE
        # =========================
        executive = await get_executive(executive_type)

        if not executive:
            await interaction.response.send_message(
                "Data executive tidak ditemukan.",
                ephemeral=True
            )
            return

        # =========================
        # GET SECTION
        # =========================
        section = await get_executive_section(
            executive_type_id=executive["id"],
            section_key=selected
        )

        # =========================
        # VALIDATION
        # =========================
        if not section:
            await interaction.response.send_message(
                "Data informasi executive tidak ditemukan.",
                ephemeral=True
            )
            return

        # =========================
        # TAMBAHKAN EXECUTIVE NAME
        # =========================
        section["executive_name"] = executive["name"]

        # =========================
        # BUILD EMBED
        # =========================
        embed = build_content_embed(section)

        # =========================
        # ACK INTERACTION
        # =========================
        await interaction.response.defer()

        # =========================
        # SOURCE OF TRUTH MESSAGE
        # =========================
        key = (
            interaction.channel.id,
            interaction.user.id
        )

        msg = self.view.info_messages.get(key)

        try:

            # =========================
            # JIKA MESSAGE SUDAH ADA → EDIT
            # =========================
            if msg:
                await msg.edit(embed=embed)

            # =========================
            # JIKA BELUM ADA → BUAT BARU
            # =========================
            else:
                msg = await interaction.channel.send(
                    embed=embed
                )

                self.view.info_messages[key] = msg

            # =========================
            # SCHEDULER RESET
            # =========================
            await register_delete(
                channel_id=msg.channel.id,
                message_id=msg.id,
                delete_after="3m"
            )

        except discord.NotFound:

            # =========================
            # MESSAGE HILANG → BUAT ULANG
            # =========================
            msg = await interaction.channel.send(
                embed=embed
            )

            self.view.info_messages[key] = msg

            await register_delete(
                channel_id=msg.channel.id,
                message_id=msg.id,
                delete_after="3m"
            )


# =========================
# VIEW
# =========================
class ExecutiveInfoView(discord.ui.View):

    def __init__(self, executive_type):

        super().__init__(timeout=None)

        self.info_messages = {}

        self.add_item(
            ExecutiveInfoSelect(executive_type)
        )
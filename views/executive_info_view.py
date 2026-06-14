import discord
import json
import os
from utils.delete_scheduler import (
    register_delete
)
from utils.json_manager import (
    load_json,
    EXECUTIVE_MESSAGES_PATH
)
    
# =========================
# BUILD CONTENT EMBED
# =========================
def build_content_embed(data):

    description = data.get("description", "")

    # =========================
    # JIKA DESCRIPTION LIST
    # =========================
    if isinstance(description, list):
        description = "\n".join(description)
    # =========================
    # JIKA KOSONG
    # =========================
    if not description or str(description).strip() == "":
        description = "Sedang dalam pembuatan."
        
    embed = discord.Embed(
        title=data.get("title", "Executive Information"),
        description=description or None,
        color=discord.Color.blurple()
    )
    
    # =========================
    # ADD FIELDS SUPPORT
    # =========================
    
    add_fields = data.get("add_field", [])
    
    if add_fields:
        for field in add_fields:
            name = field.get("name", "No Title")
            value = field.get("value", [])
            
            # =========================
            # JIKA VALUE LIST
            # =========================
            if isinstance(value, list):
                value = "\n".join(value)
            
            embed.add_field(
                name=name,
                value=value or "\u200b",
                inline=False
            )
    return embed


# =========================
# DROPDOWN SELECT
# =========================
class ExecutiveInfoSelect(discord.ui.Select):

    def __init__(self, executive_type: str):
        
        # =========================
        # BENEFIT DINAMIS
        # =========================
        if executive_type == "clan":
            benefit_emoji = "<:bytecoin:1508106694629265620>"
            benefit_label = "Benefit Executive Clan"

        elif executive_type == "guild":
            benefit_emoji = "<a:bgl:1508083038079287397>"
            benefit_label = "Benefit Executive Guild"
        
        else:
            benefit_emoji = "<a:bgl:1508083038079287397>"
            benefit_label = "Benefit Executive"

        options = [
            discord.SelectOption(
                label="Tugas Executive",
                value="tugas",
                emoji="<a:crowns2:1507955877116903516>",
                description="Lihat tugas executive"
            ),

            discord.SelectOption(
                label="Aturan Executive",
                value="aturan",
                emoji="<:gtScroll:1507973278168514661>",
                description="Lihat aturan executive"
            ),

            discord.SelectOption(
                label="Hak & Akses Executive",
                value="hak_akses",
                emoji="<a:checklist:1508081459087282237>",
                description="Lihat hak dan akses executive"
            ),

            discord.SelectOption(
                label=benefit_label,
                value="benefit",
                emoji=benefit_emoji,
                description="Lihat benefit executive"
            ),

            discord.SelectOption(
                label="Executive Promotion Guide",
                value="jenjang",
                emoji="<a:hype:1508082953740095518>",
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

        self.executive_type = executive_type

    # =========================
    # CALLBACK
    # =========================
    async def callback(self, interaction: discord.Interaction):

        # =========================
        # LOAD DATA
        # =========================
        messages = await load_json(EXECUTIVE_MESSAGES_PATH)
        selected = self.values[0]
        executive_type = self.executive_type

        data = (
            messages
            .get(executive_type, {})
            .get(selected)
        )

        # =========================
        # VALIDATION
        # =========================
        if not data:
            await interaction.response.send_message(
                "Data tidak ditemukan.",
                ephemeral=True
            )
            return

        embed = build_content_embed(data)

        # =========================
        # ACK INTERACTION
        # =========================
        await interaction.response.defer()

        # =========================
        # SOURCE OF TRUTH MESSAGE
        # =========================
        msg = self.view.info_message

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
                msg = await interaction.channel.send(embed=embed)
                self.view.info_message = msg

            # =========================
            # SCHEDULER RESET
            # =========================
            await register_delete(
                channel_id=msg.channel.id,
                message_id=msg.id,
                delete_after="3m"
            )

        except discord.NotFound:
            # message hilang → buat ulang
            msg = await interaction.channel.send(embed=embed)
            self.view.info_message = msg

            await register_delete(
                channel_id=msg.channel.id,
                message_id=msg.id,
                delete_after="3m"
            )
# =========================
# VIEW
# =========================
class ExecutiveInfoView(discord.ui.View):

    def __init__(
        self,
        executive_type: str = None
    ):

        super().__init__(timeout=None)
        
        self.info_message = None

        self.add_item(
            ExecutiveInfoSelect(executive_type=executive_type)
        )
        
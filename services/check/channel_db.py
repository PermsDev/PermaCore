import discord

from database.channel_manager import get_channels
from database.guild_message_manager import get_all_guild_messages
from database.delete_queue_manager import get_delete_queue
from database.feedback_manager import get_guild_feedbacks
from database.intro_manager import get_all_intro


# =========================
# MAIN CHECK FUNCTION
# =========================
async def check_channel_messages_db(
    bot: discord.Client,
    guild: discord.Guild,
    channel_id: int | None = None
):

    db_channels = get_channels(guild.id)

    guild_messages = get_all_guild_messages(guild.id)
    delete_queue = get_delete_queue()
    feedbacks = get_guild_feedbacks(guild.id)
    intros = get_all_intro()

    # =========================
    # ALL DATABASE INDEX
    # =========================
    all_db = []

    for m in guild_messages:
        all_db.append(("guild_message_db", m))
    for m in delete_queue:
        all_db.append(("delete_queue_db", m))
    for m in feedbacks:
        all_db.append(("feedback_db", m))
    for m in intros:
        all_db.append(("intro_db", m))

    db_index = {}

    for db_name, m in all_db:
        db_index.setdefault(str(m["message_id"]), []).append({
            "db": db_name,
            "channel_id": m["channel_id"]
        })

    # =========================
    # CHANNEL FILTER (EXCLUDE LOG)
    # =========================
    unique_channels = set()
    important_messages = set()

    for key, data in db_channels.items():

        # skip log channel
        if key == "LOG_CHANNEL":
            continue

        ch_id = data["channel_id"]
        panel_msg = data.get("panel_message")

        unique_channels.add(ch_id)

        # panel message juga dianggap penting
        if panel_msg:
            important_messages.add(int(panel_msg))

    # =========================
    # RESULT CONTAINER
    # =========================
    missing = {
        "channel_message_db": []
    }

    # =========================
    # SCAN CHANNELS
    # =========================
    for ch_id in unique_channels:

        # optional filter
        if channel_id and ch_id != channel_id:
            continue

        channel = guild.get_channel(ch_id)
        if not channel:
            continue

        try:
            async for msg in channel.history(limit=200):

                if bot.user is None:
                    continue

                if msg.author.id != bot.user.id:
                    continue

                msg_id = str(msg.id)

                # =========================
                # PANEL MESSAGE SKIP RULE
                # =========================
                is_panel = msg.id in important_messages

                # =========================
                # NOT IN ANY DB
                # =========================
                if msg_id not in db_index and not is_panel:
                    missing["channel_message_db"].append({
                        "channel": ch_id,
                        "message_id": msg.id,
                        "reason": "NOT_IN_ANY_DB"
                    })
                    continue

                # =========================
                # CHANNEL MISMATCH CHECK
                # =========================
                if msg_id in db_index:

                    for entry in db_index[msg_id]:
                        if entry["channel_id"] != ch_id:

                            missing["channel_message_db"].append({
                                "channel": ch_id,
                                "message_id": msg.id,
                                "reason": "CHANNEL_MISMATCH"
                            })
                            break

        except Exception:
            continue

    return missing


# =========================
# PAGINATION VIEW
# =========================
class ChannelCheckView(discord.ui.View):

    def __init__(self, data, guild: discord.Guild):
        super().__init__(timeout=120)

        self.data = data
        self.guild = guild

        self.page = 0
        self.per_page = 10

        self.max_page = max(0, (len(data) - 1) // self.per_page)

    def build_embed(self):

        start = self.page * self.per_page
        end = start + self.per_page
        chunk = self.data[start:end]

        embed = discord.Embed(
            title="📊 Channel Message DB Check",
            color=discord.Color.orange()
        )

        if not chunk:
            embed.description = "✅ Tidak ada masalah"
            embed.set_footer(
                text=f"Page {self.page + 1}/{self.max_page + 1}"
            )
            return embed

        lines = []

        for i, m in enumerate(chunk, start=1):

            channel_mention = f"<#{m['channel']}>"
            msg_link = f"https://discord.com/channels/{self.guild.id}/{m['channel']}/{m['message_id']}"

            lines.append(
                f"{start + i}. {channel_mention} → [Jump to Message]({msg_link})"
            )

        embed.description = "\n".join(lines)

        embed.set_footer(
            text=f"Page {self.page + 1}/{self.max_page + 1} • Total: {len(self.data)}"
        )

        return embed

    # =========================
    # BUTTON PREV
    # =========================
    @discord.ui.button(label="⬅", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):

        if self.page > 0:
            self.page -= 1

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    # =========================
    # BUTTON NEXT
    # =========================
    @discord.ui.button(label="➡", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):

        if self.page < self.max_page:
            self.page += 1

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )
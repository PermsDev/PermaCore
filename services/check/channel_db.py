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
    print("=" * 60)
    print("[Check] Loading database...")

    db_channels = await get_channels(guild.id)

    guild_messages = await get_all_guild_messages(guild.id)
    delete_queue = await get_delete_queue()
    feedbacks = await get_guild_feedbacks(guild.id)
    intros = await get_all_intro()

    print(
        f"[Check] DB Loaded | "
        f"Channels={len(db_channels)} | "
        f"Guild={len(guild_messages)} | "
        f"DeleteQueue={len(delete_queue)} | "
        f"Feedback={len(feedbacks)} | "
        f"Intro={len(intros)}"
    )

    # =========================
    # BUILD DATABASE INDEX
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

    print(f"[Check] Indexed {len(db_index)} messages.")

    # =========================
    # CHANNEL FILTER
    # =========================
    unique_channels = set()
    important_messages = set()

    for key, data in db_channels.items():

        if key == "LOG_CHANNEL":
            continue

        unique_channels.add(data["channel_id"])

        if data.get("panel_message"):
            important_messages.add(int(data["panel_message"]))

    print(f"[Check] Total channels to scan : {len(unique_channels)}")

    # =========================
    # RESULT
    # =========================
    missing = {
        "channel_message_db": []
    }

    # =========================
    # SCAN CHANNEL
    # =========================
    for ch_id in unique_channels:

        if channel_id and ch_id != channel_id:
            continue

        channel = guild.get_channel(ch_id)

        if channel is None:
            print(f"[Skip] Unknown Channel ({ch_id})")
            continue

        print()
        print("=" * 60)
        print(f"[Channel] #{channel.name}")

        checked = 0

        try:

            async for msg in channel.history(limit=200):

                if bot.user is None:
                    continue

                if msg.author.id != bot.user.id:
                    continue

                checked += 1

                msg_id = str(msg.id)

                print(f"[Discord] Message {msg.id}")

                # =========================
                # PANEL MESSAGE
                # =========================
                if msg.id in important_messages:

                    print("   ↳ PANEL MESSAGE (skip)")
                    continue

                # =========================
                # NOT FOUND
                # =========================
                if msg_id not in db_index:

                    print("   ↳ ❌ NOT FOUND IN DATABASE")

                    missing["channel_message_db"].append({
                        "channel": ch_id,
                        "message_id": msg.id,
                        "reason": "NOT_IN_ANY_DB"
                    })

                    continue

                print(f"   ↳ ✅ FOUND ({len(db_index[msg_id])} entry)")

                mismatch = False

                for entry in db_index[msg_id]:

                    db_channel = entry["channel_id"]

                    print(
                        f"      DB={entry['db']} | "
                        f"Channel={db_channel}"
                    )

                    if db_channel != ch_id:

                        mismatch = True

                        print(
                            f"      ❌ CHANNEL MISMATCH "
                            f"(Discord={ch_id})"
                        )

                        missing["channel_message_db"].append({
                            "channel": ch_id,
                            "message_id": msg.id,
                            "reason": "CHANNEL_MISMATCH"
                        })

                if not mismatch:
                    print("      ✅ CHANNEL MATCH")

            print(
                f"[Done] #{channel.name} "
                f"({checked} bot messages checked)"
            )

        except Exception as e:

            print(f"[ERROR] #{channel.name}")
            print(e)

    print()
    print("=" * 60)
    print(
        f"[Check Finished] "
        f"Total Issues = {len(missing['channel_message_db'])}"
    )
    print("=" * 60)

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

            lines.append(
                f"{start+i}. "
                f"<#{m['channel']}> → "
                f"https://discord.com/channels/"
                f"{self.guild.id}/{m['channel']}/{m['message_id']}"
            )

        embed.description = "\n".join(lines)

        embed.set_footer(
            text=f"Page {self.page+1}/{self.max_page+1} • Total {len(self.data)}"
        )

        return embed

    @discord.ui.button(label="⬅", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):

        if self.page > 0:
            self.page -= 1

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    @discord.ui.button(label="➡", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):

        if self.page < self.max_page:
            self.page += 1

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )
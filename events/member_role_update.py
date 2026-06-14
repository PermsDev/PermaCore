import discord
from database.channel_manager import get_channel
from database.emoji_manager import get_emoji
from database.role_manager import get_roles
from database.guild_message_manager import (
    get_guild_message,
    upsert_guild_message
)

# ========================
# GAME DISPLAY NAMES
# ========================
GAME_DISPLAY_NAMES = {
    "growtopia": "Growtopia",
    "pw": "Pixel World",
    "minecraft": "Minecraft",
    "mlbb": "Mobile Legend",
    "roblox": "Roblox"
}

# =========================
# ROLE UTILITIES (FIXED)
# =========================
def has_pangkat(member: discord.Member, role_groups: dict) -> bool:
    member_role_ids = {r.id for r in member.roles}

    pangkat_group = role_groups.get("by_group", {}).get("pangkat", {})

    for role_id in pangkat_group.values():
        if role_id in member_role_ids:
            return True

    return False


def has_role_group_change(before, after, role_groups: dict):

    before_ids = {r.id for r in before.roles}
    after_ids = {r.id for r in after.roles}

    tracked = set()

    # pakai struktur yang benar: by_group
    for group_name, group in role_groups.get("by_group", {}).items():

        if group_name == "pangkat":
            continue

        for role_id in group.values():
            if role_id:
                tracked.add(int(role_id))

    return bool((before_ids ^ after_ids) & tracked)


def get_changed_roles(before, after):
    return {r.id for r in before.roles} ^ {r.id for r in after.roles}


# =========================
# BUILD EMBED (FIXED SAFE)
# =========================
def build_welcome_embed(member: discord.Member, role_groups: dict):

    member_role_ids = {r.id for r in member.roles}

    groups = role_groups.get("by_group", {})  # 🔥 FIX UTAMA

    gender = None
    age_group = None
    pangkat = None
    executive = None

    special_roles = []
    games = []

    # =========================
    # GENDER
    # =========================
    for name, role_id in groups.get("gender", {}).items():
        if role_id in member_role_ids:
            if name == "male":
                gender = f"{get_emoji('male')} Laki-Laki"
            elif name == "female":
                gender = f"{get_emoji('female')} Perempuan"

    # =========================
    # AGE GROUP
    # =========================
    for name, role_id in groups.get("age_group", {}).items():
        if role_id in member_role_ids:
            if name == "adult":
                age_group = "🎓 Adult"
            elif name == "children":
                age_group = "🧸 Children"

    # =========================
    # PANGKAT
    # =========================
    highest = None

    for name, role_id in groups.get("pangkat", {}).items():
        if role_id in member_role_ids:
            role = member.guild.get_role(role_id)
            if role and (highest is None or role.position > highest.position):
                highest = role

    if highest:
        pangkat = highest.mention

    # =========================
    # EXECUTIVE
    # =========================
    for name, role_id in groups.get("executive", {}).items():
        if role_id in member_role_ids:
            role = member.guild.get_role(role_id)
            if role:
                executive = role.mention

    # =========================
    # SPECIAL
    # =========================
    for name, role_id in groups.get("special", {}).items():
        if role_id in member_role_ids:
            special_roles.append(name.replace("_", " ").title())

    # =========================
    # GAMES
    # =========================
    for name, role_id in groups.get("games", {}).items():
        if role_id in member_role_ids:
            emoji = get_emoji(name)
            display = GAME_DISPLAY_NAMES.get(name, name.title())
            games.append(f"{emoji} {display}")
    # =========================
    # EMBED
    # =========================
    embed = discord.Embed(
        title="📢 Announcement..!!!",
        description=(
            f"Hallo {member.mention},\n"
            f"Selamat Datang dan Selamat Bergabung di **{member.guild.name}** 🎉\n\n"
            f"`Gender    :` {gender}\n"
            f"`Age Group :` {age_group}"
        ),
        color=discord.Color.blurple()
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    if pangkat:
        embed.add_field(name="Pangkat Discord", value=pangkat, inline=True)

    if executive:
        embed.add_field(name="Executive", value=executive, inline=True)

    if special_roles:
        embed.add_field(
            name="Special Role",
            value=", ".join(special_roles),
            inline=False
        )

    if games:
        embed.add_field(
            name="Games",
            value="\n".join(f"{i+1}. {g}" for i, g in enumerate(games)),
            inline=False
        )

    embed.set_footer(
        text=f"{member.guild.name} | Joined at: {member.joined_at.strftime('%d %B %Y')}",
        icon_url=member.guild.icon.url if member.guild.icon else None
    )

    return embed


# =========================
# PROCESS WELCOME (FIXED DB SAFE)
# =========================
async def process_welcome(member: discord.Member):

    guild = member.guild

    channel_data = get_channel(guild.id, "WELCOME_CHANNEL")
    if not channel_data:
        return

    channel = guild.get_channel(int(channel_data["channel_id"]))
    if not channel:
        return

    role_groups = get_roles(guild.id)

    embed = build_welcome_embed(member, role_groups)

    msg = get_guild_message(guild.id, member.id, "welcome")
    message_id = msg["message_id"] if msg else None

    if message_id:
        try:
            message = await channel.fetch_message(int(message_id))
            await message.edit(embed=embed)
            return
        except (discord.NotFound, discord.Forbidden):
            pass

    message = await channel.send(embed=embed)

    upsert_guild_message(
        guild.id,
        member.id,
        "welcome",
        channel.id,
        message.id
    )
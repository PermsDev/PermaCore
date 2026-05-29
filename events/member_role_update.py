import discord
from utils.json_manager import (
    GUILD_SETTINGS_PATH,
    ROLE_GROUPS_PATH,
    GUILD_MESSAGES_PATH,
    load_json,
    save_json
)

# =========================
# GAME EMOJIS
# =========================
GAME_EMOJIS = {
    "growtopia": "<:growtopia:1501506623007494184>",
    "pw": "<:pw:1501515036638707712>",
    "minecraft": "<:minecraft:1501515510724952204>",
    "mlbb": "<:mlbb:1501920972582686891>",
    "roblox": "<:roblox:1501521251167113247>"
}

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
# GET WELCOME CHANNEL
# =========================
async def get_welcome_channel_id(
    guild_id: int
):

    data = await load_json(
        GUILD_SETTINGS_PATH
    )

    guild_data = data.get(
        str(guild_id),
        {}
    )

    return guild_data.get(
        "welcome_channel_id"
    )

# =========================
# GET ROLE DATA
# =========================
async def get_role_groups(
    guild_id: int
):

    data = await load_json(
        ROLE_GROUPS_PATH
    )

    return data.get(
        str(guild_id),
        {}
    )

def has_pangkat(member: discord.Member, role_groups: dict) -> bool:
    member_role_ids = {role.id for role in member.roles}

    for role_id in role_groups.get("pangkat", {}).values():
        if role_id in member_role_ids:
            return True

    return False

def has_role_group_change(before: discord.Member, after: discord.Member, role_groups: dict) -> bool:
    before_roles = {r.id for r in before.roles}
    after_roles = {r.id for r in after.roles}

    tracked = set()

    for group_name, group in role_groups.items():
        if group_name == "pangkat":
            continue  # pangkat bukan trigger perubahan
        tracked.update(group.values())

    return len((before_roles ^ after_roles) & tracked) > 0

def get_changed_roles(before, after):
    return {r.id for r in before.roles} ^ {r.id for r in after.roles}

# =========================
# BUILD EMBED
# =========================
def build_welcome_embed(
    member: discord.Member,
    role_groups: dict
):

    member_role_ids = {
        role.id
        for role in member.roles
    }

    gender = None
    age_group = None
    pangkat = None
    executive = None

    special_roles = []
    games = []

    # =========================
    # GENDER
    # =========================
    for name, role_id in role_groups.get(
        "gender",
        {}
    ).items():

        if role_id in member_role_ids:

            if name == "male":
                gender = "<:mans:1508478159832612986>  Laki-Laki"

            elif name == "female":
                gender = "<:girls:1508477653299236937>  Perempuan"
                
    # =========================
    # AGE GROUP
    # =========================
    for name, role_id in role_groups.get(
        "age_group",
        {}
    ).items():
        
        if role_id in member_role_ids:
            
            if name == "adult":
                age_group = "🎓  Adult"
                
            elif name == "children":
                age_group = "🧸  Children"
                
    # =========================
    # PANGKAT
    # =========================
    highest_pangkat_role = None

    for name, role_id in role_groups.get(
        "pangkat",
        {}
    ).items():

        if role_id in member_role_ids:

            role = member.guild.get_role(role_id)

            if role:

                if (
                    highest_pangkat_role is None
                    or role.position > highest_pangkat_role.position
                ):
                    highest_pangkat_role = role

    if highest_pangkat_role:
        pangkat = highest_pangkat_role.mention

    # =========================
    # EXECUTIVE
    # =========================
    for name, role_id in role_groups.get(
        "executive",
        {}
    ).items():

        if role_id in member_role_ids:

            role = member.guild.get_role(role_id)

            if role:
                executive = role.mention

    # =========================
    # SPECIAL
    # =========================
    for name, role_id in role_groups.get(
        "special",
        {}
    ).items():
        
        if role_id in member_role_ids:
            
            special_roles.append(
                name.replace("_", " ").title()
            )

    # =========================
    # GAMES
    # =========================
    for name, role_id in role_groups.get(
        "games",
        {}
    ).items():

        if role_id in member_role_ids:

            emoji = GAME_EMOJIS.get(
                name,
                "🎯"
            )

            display_name = GAME_DISPLAY_NAMES.get(
                name,
                name.title()
            )

            games.append(
                f"{emoji} "
                f"{display_name}"
            )

    # =========================
    # EMBED
    # =========================
    embed = discord.Embed(
        title="📢 Announcement..!!!",
        description=(
            f"Hallo {member.mention}, \n"
            f"Selamat datang dan selamat bergabung di **{member.guild.name}**! 🎉\n\n"

            f"`Gender    :` {gender}\n"
            f"`Age Group :` {age_group}"
        ),
        color=discord.Color.blurple()
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    # =========================
    # FIELDS
    # =========================
        
    if pangkat:
        
        embed.add_field(
            name="Pangkat Discord",
            value=pangkat,
            inline=True
        )
        
    if executive:

        embed.add_field(
            name="Executive",
            value=executive,
            inline=True
        )

    if special_roles:

        embed.add_field(
            name="Special Role",
            value=", ".join(
                special_roles
            ),
            inline=False
        )

    if games:
        formatted_games = "\n".join(
            f"{i+1}. {game}"
            for i, game in enumerate(games)
        )

        embed.add_field(
            name="Games",
            value=formatted_games,
            inline=False
        )

    embed.set_footer(
        text=(
            f"{member.guild.name} | "
            f"Joined at: "
            f"{member.joined_at.strftime('%d %B %Y')}"
        ),
        icon_url=member.guild.icon.url
        if member.guild.icon
        else None
    )

    return embed


# =========================
# PROCESS WELCOME
# =========================
async def process_welcome(
    member: discord.Member
):

    guild = member.guild

    # =========================
    # LOAD SETTINGS
    # =========================
    channel_id = await get_welcome_channel_id(
        guild.id
    )

    if not channel_id:
        return

    channel = guild.get_channel(
        int(channel_id)
    )

    if not channel:
        return

    # =========================
    # ROLE GROUPS
    # =========================
    role_groups = await get_role_groups(
        guild.id
    )

    # =========================
    # BUILD EMBED
    # =========================
    embed = build_welcome_embed(
        member,
        role_groups
    )

    # =========================
    # LOAD MESSAGE CACHE
    # =========================
    data = await load_json(
        GUILD_MESSAGES_PATH
    )

    guild_data = data.setdefault(
        str(guild.id),
        {}
    )

    user_id = str(member.id)

    user_data = guild_data.setdefault(user_id, {})
    welcome_data = user_data.setdefault("welcome", {})
    message_id = welcome_data.get("message_id")

    # =========================
    # EDIT EXISTING MESSAGE
    # =========================
    if message_id:

        try:

            message = await channel.fetch_message(
                int(message_id)
            )

            await message.edit(
                embed=embed
            )

            return

        except discord.NotFound:
            pass

    # =========================
    # SEND NEW MESSAGE
    # =========================
    message = await channel.send(
        embed=embed
    )

    welcome_data["message_id"] = message.id
    welcome_data["channel_id"] = channel.id

    await save_json(
        GUILD_MESSAGES_PATH,
        data
    )

import discord
from database.core.emoji_manager import get_emoji


def create_guild_manage_panel() -> discord.Embed:
    GUILD_LOCK = get_emoji("guild_lock")
    print(GUILD_LOCK)

    embed = discord.Embed(
        description=(
            f"# {GUILD_LOCK} Guild Management\n\n"
            "Panel pengelolaan guild untuk Executive.\n\n"
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="🏆 Top Clash Guild",
        value=(
            "Tambahkan atau edit member guild yang terdaftar di Top Clash Guilds bulan ini."
        ),
        inline=False
    )

    embed.add_field(
        name="🔑 Edit Door Password",
        value=(
            "Kelola password untuk hadiah top clash member guild. password akan diberikan kepada member yang masuk Top Clash Guilds bulan ini."
        ),
        inline=False
    )

    embed.set_footer(
        text="Guild Management • Executive Panel"
    )

    return embed
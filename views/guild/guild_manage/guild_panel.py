import discord
from database.core.emoji_manager import get_emoji


def create_guild_manage_panel() -> discord.Embed:

    embed = discord.Embed(
        description=(
            f"# {get_emoji('guild_lock')} Guild Management\n\n"
            "Panel pengelolaan guild untuk Executive.\n\n"
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name=f"{get_emoji('rank_1')} Top Clash Guild",
        value=(
            "-# Tambahkan atau edit member guild yang terdaftar di Top Clash Guilds bulan ini."
        ),
        inline=False
    )

    embed.add_field(
        name=f"{get_emoji('password_door')} Change Password",
        value=(
            "-# Kelola password untuk hadiah top clash member guild. password akan diberikan kepada member yang masuk Top Clash Guilds bulan ini."
        ),
        inline=False
    )

    embed.set_footer(
        text="Guild Management • Executive Panel"
    )

    return embed
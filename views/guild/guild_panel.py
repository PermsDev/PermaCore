import discord


def create_guild_manage_panel() -> discord.Embed:

    embed = discord.Embed(
        title="Guild Management",
        description=(
            "Panel pengelolaan guild untuk Executive.\n\n"
            "Gunakan tombol di bawah untuk mengakses "
            "berbagai fitur pengelolaan guild."
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="Top Clash Guilds",
        value=(
            "Tambahkan atau edit member guild yang terdaftar di Top Clash Guilds bulan ini."
        ),
        inline=False
    )

    embed.add_field(
        name="Edit Door Password",
        value=(
            "Kelola password untuk hadiah top clash member guild. password akan diberikan kepada member yang masuk Top Clash Guilds bulan ini."
        ),
        inline=False
    )

    embed.set_footer(
        text="Guild Management • Executive Panel"
    )

    return embed
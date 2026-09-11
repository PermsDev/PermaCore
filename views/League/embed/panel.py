import discord

def create_league_panel() -> discord.Embed:

    return discord.Embed(
        title="🏆 Perma Community League",
        description=(
            "Informasi dan pendaftaran League"
            "akan tersedia di sini!"
        ),
        color=discord.Color.blue()
    )

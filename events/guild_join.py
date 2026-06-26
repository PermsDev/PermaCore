import discord

async def handle_guild_join(guild: discord.Guild):
    print(f"Bot bergabung ke server: {guild.name} ({guild.id})")
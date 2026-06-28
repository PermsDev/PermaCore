import discord


# ==================================================
# GET TARGET GUILD
# ==================================================
async def get_target_guild(
    bot,
    interaction: discord.Interaction,
    guild_id: str | None
):

    # gunakan guild tempat command dijalankan
    if guild_id is None:
        return interaction.guild

    guild = bot.get_guild(int(guild_id))

    if guild is None:
        raise ValueError(
            "Guild tidak ditemukan atau bot tidak berada di guild tersebut."
        )

    return guild


# ==================================================
# GET TARGET MEMBERS
# ==================================================
async def get_target_members(
    guild: discord.Guild,
    user: discord.Member | None
):

    # hanya satu user
    if user is not None:
        return [user]

    # seluruh member guild
    return [
        member
        for member in guild.members
        if not member.bot
    ]
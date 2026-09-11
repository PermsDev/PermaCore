import discord

def get_executive_welcome_embed(
    member,
    role
):

    embed = discord.Embed(
        title="🎉 Welcome Executive",
        description=(
            f"Selamat {member.mention}!\n\n"
            f"Kamu sekarang menjadi "
            f"``{role.name}``.\n\n"
            f"Silakan baca seluruh "
            f"informasi executive melalui "
            f"dropdown di bawah."
        ),
        color=discord.Color.green()
    )

    return embed
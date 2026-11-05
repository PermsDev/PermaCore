import re
import discord

from discord import app_commands
from discord.ext import commands

from database.core.emoji_manager import set_emoji


class Emoji(commands.GroupCog, group_name="emoji"):

    @app_commands.command(
        name="add",
        description="Add or update a custom emoji"
    )
    async def add(
        self,
        interaction: discord.Interaction,
        emoji: str
    ):

        match = re.fullmatch(
            r"<(a?):([A-Za-z0-9_]{2,32}):(\d+)>",
            emoji.strip()
        )

        if not match:

            await interaction.response.send_message(
                "❌ Invalid custom emoji format.\n"
                "Use `<:name:id>` or `<a:name:id>`.",
                ephemeral=True
            )
            return

        animated = bool(match.group(1))
        emoji_key = match.group(2)
        emoji_id = int(match.group(3))

        try:

            await set_emoji(
                emoji_key=emoji_key,
                emoji_id=emoji_id,
                animated=animated
            )

            emoji_format = (
                f"<a:{emoji_key}:{emoji_id}>"
                if animated
                else f"<:{emoji_key}:{emoji_id}>"
            )

            await interaction.response.send_message(
                f"✅ Successfully added/updated emoji {emoji_format}\n\n"
                f"**Key:** `{emoji_key}`\n"
                f"**ID:** `{emoji_id}`\n"
                f"**Animated:** `{animated}`",
                ephemeral=True
            )

        except Exception as e:

            print(f"[EMOJI ADD ERROR] {e}")

            await interaction.response.send_message(
                "❌ Failed to save emoji.",
                ephemeral=True
            )


async def setup(bot):

    await bot.add_cog(Emoji())
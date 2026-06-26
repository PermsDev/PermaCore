import discord

from discord import app_commands
from discord.ext import commands


class AboutView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(
            discord.ui.Button(
                label="Join Community",
                emoji="🌐",
                url="https://discord.gg/weAkeanQc4"
            )
        )


class About(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="about",
        description="Informasi mengenai PermaCore."
    )
    async def about(
        self,
        interaction: discord.Interaction
    ):

        embed = discord.Embed(
            title="🤖 PermaCore",
            description=(
                "PermaCore adalah bot Discord multifungsi yang "
                "dirancang untuk membantu pengelolaan komunitas "
                "dengan berbagai fitur administrasi, utilitas, "
                "dan otomatisasi."
            ),
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="✨ Fitur",
            value=(
                "• Slash Commands\n"
                "• Utility Commands\n"
                "• Community Management\n"
                "• Automation System"
            ),
            inline=False
        )

        embed.add_field(
            name="🌐 Status",
            value=(
                f"**Servers:** {len(self.bot.guilds)}\n"
                f"**Users:** {sum(g.member_count or 0 for g in self.bot.guilds):,}"
            ),
            inline=True
        )

        embed.add_field(
            name="⚙️ Teknologi",
            value=(
                "Python\n"
                "discord.py"
            ),
            inline=True
        )

        embed.set_footer(
            text="PermaCore"
        )

        await interaction.response.send_message(
            embed=embed,
            view=AboutView(),
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(
        About(bot)
    )
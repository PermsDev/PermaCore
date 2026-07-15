import discord, os
from discord import app_commands
from discord.ext import commands

from services.check.channel_db import check_channel_messages_db, ChannelCheckView
from services.check.message_db import check_message_db
from services.check.member_db import check_member_db
from services.check.cleanup.message_db_cleanup import cleanup_message_db

OWNER_ID = int(os.getenv("OWNER_ID"))

def is_owner(interaction: discord.Interaction) -> bool:
    return interaction.user.id == OWNER_ID

class CheckGroup(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CheckFailure):

            if interaction.response.is_done():
                await interaction.followup.send(
                    "❌ Hanya developer yang dapat menggunakan command ini.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ Hanya developer yang dapat menggunakan command ini.",
                    ephemeral=True
                )
                
    check = app_commands.Group(
        name="check",
        description="Check database tools"
    )

    # =========================
    # /check channel
    # =========================
    @check.command(
        name="channel",
        description="(Only Developer) Check message bot di channel vs database"
    )
    @app_commands.check(is_owner)
    async def check_channel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel | None = None
    ):

        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        result = await check_channel_messages_db(
            self.bot,
            interaction.guild,
            channel_id=channel.id if channel else None
        )

        missing = result["channel_message_db"]

        if not missing:
            await interaction.followup.send(
                "✅ Semua message bot sudah sesuai database.",
                ephemeral=True
            )
            return

        view = ChannelCheckView(missing, interaction.guild)

        await interaction.followup.send(
            embed=view.build_embed(),
            view=view,
            ephemeral=True
        )

    # =========================
    # /check message_db
    # =========================
    @check.command(
        name="database", 
        description="(Only Developer) Check message bot di database vs channel"
    )
    @app_commands.check(is_owner)
    @app_commands.describe(messages="Optional: pilih DB yang mau dicek")
    @app_commands.choices(messages=[
        app_commands.Choice(name="All Messages", value="all"),
        app_commands.Choice(name="DM Messages", value="dm_message_db"),
        app_commands.Choice(name="Delete Queue Messages", value="delete_queue_db"),
        app_commands.Choice(name="Feedback Messages", value="feedback_db"),
        app_commands.Choice(name="Guild Messages", value="guild_message_db"),
        app_commands.Choice(name="Intro Messages", value="intro_db"),
        app_commands.Choice(name="Channel Panel", value="channel_db"),
    ])
    async def message_db(
        self,
        interaction: discord.Interaction,
        messages: app_commands.Choice[str] | None = None
    ):

        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        selected = messages.value if messages else None
        if selected == "all":
            selected = None

        missing = await check_message_db(
            self.bot,
            guild,
            messages=selected
        )

        # =========================
        # FILTER ONLY ISSUES
        # =========================
        total_issues = sum(len(v) for v in missing.values())

        if total_issues == 0:
            return await interaction.followup.send(
                "✅ Tidak ada masalah di database.",
                ephemeral=True
            )

        embed = discord.Embed(
            title="📊 Message DB Issues Found",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="Mode",
            value=selected or "ALL",
            inline=False
        )

        for k, v in missing.items():
            if not v:
                continue

            # channel_db menyimpan dict
            if k == "channel_db":
                lines = []

                for item in v:
                    line = (
                        f"• `{item['key']}`\n"
                        f"Channel: `{item['channel_id']}`\n"
                        f"Reason: `{item['reason']}`"
                    )

                    if "panel_message" in item:
                        line += f"\nMessage: `{item['panel_message']}`"

                    lines.append(line)

                value = "\n\n".join(lines)

            else:
                # database lain menyimpan list message_id
                value = "\n".join(
                    f"• `{message_id}`"
                    for message_id in v
                )

            # Discord maksimal 1024 karakter per field
            if len(value) > 1024:
                value = value[:1000] + "\n..."

            embed.add_field(
                name=f"{k} ({len(v)})",
                value=value,
                inline=False
            )
        embed.set_footer(text="Apakah kamu ingin menghapus data ini dari database?")

        # =========================
        # CONFIRM BUTTON
        # =========================
        class ConfirmView(discord.ui.View):

            def __init__(self):
                super().__init__(timeout=30)

            @discord.ui.button(label="Delete DB", style=discord.ButtonStyle.danger)
            async def delete(self, interaction_btn: discord.Interaction, button: discord.ui.Button):

                await interaction_btn.response.defer(ephemeral=True)

                deleted = await cleanup_message_db(missing)

                await interaction_btn.followup.send(
                    f"🗑️ Deleted {deleted} entries from database.",
                    ephemeral=True
                )

                self.stop()

            @discord.ui.button(label="Keep Data", style=discord.ButtonStyle.secondary)
            async def keep(self, interaction_btn: discord.Interaction, button: discord.ui.Button):

                await interaction_btn.response.send_message(
                    "👍 Data tidak dihapus.",
                    ephemeral=True
                )

                self.stop()

        await interaction.followup.send(
            embed=embed,
            view=ConfirmView(),
            ephemeral=True
        )

    # =========================
    # /check member
    # =========================
    @check.command(
        name="member",
        description="(Only Developer) Check guild members vs user_db"
    )
    @app_commands.check(is_owner)
    async def member(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.defer(ephemeral=True)

        result = await check_member_db(interaction.guild)

        if not result["orphan"]:

            embed = discord.Embed(
                title="✅ Member Check Complete",
                color=discord.Color.green()
            )

        else:

            embed = discord.Embed(
                title="⚠️ Member Check Complete",
                color=discord.Color.orange()
            )

        embed.add_field(
            name="Discord Members",
            value=str(result["discord"])
        )

        embed.add_field(
            name="Database Users",
            value=str(result["database"])
        )

        embed.add_field(
            name="Added",
            value=str(len(result["added"])),
            inline=False
        )

        if result["orphan"]:

            text = "\n".join(
                f"• `{user_id}`"
                for user_id in result["orphan"][:30]
            )

            if len(result["orphan"]) > 30:
                text += f"\n... dan {len(result['orphan']) - 30} lainnya"

            embed.add_field(
                name=f"Orphan Users ({len(result['orphan'])})",
                value=text,
                inline=False
            )

        else:

            embed.add_field(
                name="Status",
                value="✅ Semua member sudah sinkron.",
                inline=False
            )

        await interaction.followup.send(
            embed=embed,
            ephemeral=True
        )
    
async def setup(bot):
    await bot.add_cog(CheckGroup(bot))
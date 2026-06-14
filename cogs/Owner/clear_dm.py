import os
import asyncio
import discord
from discord.ext import commands
from discord import app_commands

from database.dm_message_manager import get_dm_message
from utils.logger import send_log

OWNER_ID = int(os.getenv("OWNER_ID"))

# =========================
# PROTECTED DM TYPES
# =========================
PROTECTED_DM_TYPES = {
    "executive",
    "welcome",
    "intro"
}


class ClearDM(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="clearbotdm",
        description="Hapus DM bot (kecuali protected)"
    )
    @app_commands.check(
        lambda interaction: interaction.user.id == OWNER_ID
    )
    async def clear_bot_dm(
        self,
        interaction: discord.Interaction,
        user: discord.Member = None,
        role: discord.Role = None
    ):

        await interaction.response.send_message(
            "Mulai menghapus DM bot...",
            ephemeral=True
        )

        deleted = 0
        failed = 0
        skipped = 0

        guild = interaction.guild

        # ======================
        # TARGET MEMBERS
        # ======================
        if user is not None:
            targets = [user]

        elif role is not None:
            targets = [m for m in role.members if not m.bot]

        else:
            targets = [m for m in guild.members if not m.bot]

        # ======================
        # START CLEANING
        # ======================
        for member in targets:

            try:
                dm = member.dm_channel

                if dm is None:
                    dm = await member.create_dm()

                async for message in dm.history(limit=None):

                    # hanya pesan bot
                    if message.author.id != self.bot.user.id:
                        continue

                    # ======================
                    # CHECK PROTECTED IDS (MULTI TYPE)
                    # ======================
                    is_protected = False

                    for dm_type in PROTECTED_DM_TYPES:

                        protected_id = get_dm_message(
                            guild.id,
                            member.id,
                            dm_type
                        )

                        if protected_id and message.id == protected_id:
                            is_protected = True
                            break

                    if is_protected:
                        skipped += 1
                        print(
                            f"[SKIP PROTECTED] "
                            f"user={member} msg_id={message.id}"
                        )
                        continue

                    # ======================
                    # DELETE MESSAGE
                    # ======================
                    try:
                        print(
                            f"[DELETE] user={member} msg_id={message.id}"
                        )

                        await message.delete()
                        deleted += 1

                        await asyncio.sleep(0.5)

                    except discord.NotFound:
                        # sudah tidak ada
                        continue

                    except discord.Forbidden:
                        failed += 1
                        print(f"[FORBIDDEN] {member}")
                        break

                    except Exception as e:
                        failed += 1
                        print(f"[ERROR DELETE] {e}")

            except Exception as e:
                failed += 1
                print(f"[FAILED USER] {member} | {e}")

        # ======================
        # RESULT
        # ======================
        await interaction.followup.send(
            f"✅ Selesai Clear DM\n\n"
            f"Target user: {len(targets)}\n"
            f"Pesan dihapus: {deleted}\n"
            f"Protected skipped: {skipped}\n"
            f"Gagal: {failed}",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(ClearDM(bot))
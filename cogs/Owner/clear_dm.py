import os
import asyncio

import discord
from discord.ext import commands
from discord import app_commands

from utils.json_manager import (
    DM_MESSAGES_PATH,
    load_json
)

OWNER_ID = int(
    os.getenv("OWNER_ID")
)


class ClearDM(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    @app_commands.command(
        name="clearbotdm",
        description="Hapus DM bot"
    )

    @app_commands.check(
        lambda interaction:
        interaction.user.id == OWNER_ID
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
        # LOAD PROTECTED DM IDS
        # ======================
        protected_data = await load_json(
            DM_MESSAGES_PATH
        )

        protected_dm_ids = set()

        try:

            for guild_id, users in (
                protected_data.items()
            ):

                for user_id, data in (
                    users.items()
                ):

                    executive_dm_id = data.get(
                        "executive_dm_id"
                    )

                    if executive_dm_id:

                        protected_dm_ids.add(
                            int(executive_dm_id)
                        )

        except Exception as e:

            print(
                f"[FAILED LOAD PROTECTED IDS] "
                f"{e}"
            )

        print(
            f"[PROTECTED IDS] "
            f"{protected_dm_ids}"
        )

        # ======================
        # TARGET MEMBERS
        # ======================
        targets = []

        # user spesifik
        if user is not None:

            targets = [user]

        # role spesifik
        elif role is not None:

            targets = [
                member
                for member in role.members
                if not member.bot
            ]

        # semua member
        else:

            targets = [
                member
                for member in guild.members
                if not member.bot
            ]

        print(
            "\n===== START CLEAR BOT DM =====\n"
        )

        for member in targets:

            print(
                f"[CHECK USER] {member}"
            )

            try:

                dm = member.dm_channel

                if dm is None:

                    dm = await member.create_dm()

                async for message in dm.history(
                    limit=None
                ):

                    # ======================
                    # HANYA PESAN BOT
                    # ======================
                    if (
                        message.author.id
                        != self.bot.user.id
                    ):

                        continue

                    # ======================
                    # SKIP EXECUTIVE DM
                    # ======================
                    if (
                        message.id
                        in protected_dm_ids
                    ):

                        skipped += 1

                        print(
                            f"[SKIP EXECUTIVE DM] "
                            f"user={member} | "
                            f"msg_id={message.id}"
                        )

                        continue

                    try:

                        content = (
                            message.content[:80]
                            if message.content
                            else "[EMBED/EMPTY]"
                        )

                        print(
                            f"[DELETE] "
                            f"user={member} | "
                            f"msg_id={message.id} | "
                            f"content='{content}'"
                        )

                        await message.delete()

                        print(
                            f"[SUCCESS] "
                            f"Deleted {message.id}"
                        )

                        deleted += 1

                        # ======================
                        # ANTI RATE LIMIT
                        # ======================
                        await asyncio.sleep(0.5)

                    except Exception as e:

                        failed += 1

                        print(
                            f"[FAILED DELETE] "
                            f"user={member} | "
                            f"msg_id={message.id} | "
                            f"error={e}"
                        )

            except Exception as e:

                failed += 1

                print(
                    f"[FAILED USER] "
                    f"user={member} | "
                    f"error={e}"
                )

        print(
            "\n===== FINISHED CLEAR BOT DM =====\n"
        )

        await interaction.followup.send(
            f"Selesai.\n\n"
            f"Target user: {len(targets)}\n"
            f"Pesan dihapus: {deleted}\n"
            f"Executive DM di-skip: {skipped}\n"
            f"Gagal: {failed}",
            ephemeral=True
        )


async def setup(bot):

    await bot.add_cog(
        ClearDM(bot)
    )
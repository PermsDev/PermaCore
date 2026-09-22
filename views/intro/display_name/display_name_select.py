import discord

from database.main.user.display_name_manager import (
    set_display_source
)

from services.display_name.get_display_name import (
    get_display_name
)

from services.display_name.update_display_name import (
    update_display_name
)


class DisplayNameSelect(discord.ui.Select):

    def __init__(self):

        options = [
            discord.SelectOption(
                label="Nickname",
                value="nickname",
                description="Gunakan nickname Discord kamu.",
                emoji="👤"
            ),
            discord.SelectOption(
                label="GrowID",
                value="growid",
                description="Gunakan GrowID kamu.",
                emoji="🌱"
            ),
            discord.SelectOption(
                label="Roblox Username",
                value="roblox",
                description="Gunakan username Roblox kamu.",
                emoji="🎮"
            )
        ]

        super().__init__(
            placeholder="Pilih display name...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="display_name_select"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        guild_id = interaction.guild.id
        user_id = interaction.user.id

        display_source = self.values[0]

        # ======================
        # SAVE DISPLAY SOURCE
        # ======================

        await set_display_source(
            guild_id=guild_id,
            user_id=user_id,
            display_source=display_source
        )

        # ======================
        # GET DISPLAY NAME
        # ======================

        display_name = await get_display_name(
            guild_id=guild_id,
            user_id=user_id
        )

        # ======================
        # DISPLAY NAME LABEL
        # ======================

        display_names = {
            "nickname": "Nickname",
            "growid": "GrowID",
            "roblox": "Roblox Username"
        }

        display_name_label = display_names.get(
            display_source,
            display_source
        )

        # ======================
        # DATA TIDAK TERSEDIA
        # ======================

        if not display_name:

            await interaction.response.edit_message(
                content=(
                    "❌ Tidak dapat menggunakan display name tersebut.\n"
                    f"Data **{display_name_label}** belum tersedia."
                ),
                view=None
            )

            return

        # ======================
        # UPDATE DISCORD NICKNAME
        # ======================

        rename_success = await update_display_name(
            interaction.user
        )

        # ======================
        # RENAME FAILED
        # ======================

        if not rename_success:

            await interaction.response.edit_message(
                content=(
                    "⚠️ Pilihan display name berhasil disimpan,\n"
                    "tetapi nickname Discord tidak dapat diubah "
                    "karena permission/role."
                ),
                view=None
            )

            return

        # ======================
        # SUCCESS
        # ======================

        await interaction.response.edit_message(
            content=(
                "✅ Display name berhasil diubah.\n"
                f"**Sumber:** {display_name_label}\n"
                f"**Sekarang menggunakan:** `{display_name}`"
            ),
            view=None
        )
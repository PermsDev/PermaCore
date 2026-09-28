import discord

from database.guild.door_password_manager import (
    get_door_password,
    update_door_shared
)


class DoorPasswordDMView(discord.ui.View):

    def __init__(
        self,
        target_user: discord.User,
        pass_id: int,
        owner_id: int
    ):
        super().__init__(timeout=300)

        self.target_user = target_user
        self.pass_id = pass_id
        self.owner_id = owner_id

    async def interaction_check(
        self,
        interaction: discord.Interaction
    ) -> bool:

        if interaction.user.id != self.owner_id:

            await interaction.response.send_message(
                "❌ Hanya pengguna yang membuat data ini "
                "yang dapat menggunakannya.",
                ephemeral=True
            )

            return False

        return True

    @discord.ui.button(
        label="Kirim Password",
        emoji="📩",
        style=discord.ButtonStyle.success,
        custom_id="guild_manage:door_password_send"
    )
    async def send_password_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.defer(
            ephemeral=True
        )

        guild_id = interaction.guild.id

        door = await get_door_password(
            guild_id=guild_id,
            pass_id=self.pass_id
        )

        if door is None:

            await interaction.followup.send(
                "❌ Data door tidak ditemukan.",
                ephemeral=True
            )

            return

        if door["pass_door"] is None:

            await interaction.followup.send(
                "❌ Password door belum tersedia.",
                ephemeral=True
            )

            return

        try:

            await self.target_user.send(
                f"**🔐 Door Password**\n\n"
                f"World: `{door['world_name']}`\n"
                f"Door: `{door['name_door']}`\n"
                f"Password: `{door['pass_door']}`"
            )

        except discord.Forbidden:

            await interaction.followup.send(
                f"❌ Tidak dapat mengirim DM kepada "
                f"{self.target_user.mention}.",
                ephemeral=True
            )

            return

        except discord.HTTPException:

            await interaction.followup.send(
                "❌ Gagal mengirim password melalui DM.",
                ephemeral=True
            )

            return

        await update_door_shared(
            guild_id=guild_id,
            pass_id=self.pass_id
        )

        for child in self.children:
            child.disabled = True

        await interaction.edit_original_response(
            content=(
                "✅ **Password berhasil dikirim melalui DM.**\n\n"
                f"World: `{door['world_name']}`\n"
                f"Door: `{door['name_door']}`\n"
                f"Penerima: {self.target_user.mention}"
            ),
            view=self
        )
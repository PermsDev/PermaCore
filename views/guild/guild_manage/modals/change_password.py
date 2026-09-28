# python
import discord

from database.guild.door_password_manager import update_door_password


class ChangePasswordModal(discord.ui.Modal):

    def __init__(self):

        super().__init__(
            title="Change Door Password"
        )

        self.password_1 = discord.ui.TextInput(
            label="Password 1",
            placeholder="Password ID 1",
            required=False,
            max_length=100
        )

        self.password_2 = discord.ui.TextInput(
            label="Password 2",
            placeholder="Password ID 2",
            required=False,
            max_length=100
        )

        self.password_3 = discord.ui.TextInput(
            label="Password 3",
            placeholder="Password ID 3",
            required=False,
            max_length=100
        )

        self.password_4 = discord.ui.TextInput(
            label="Password 4",
            placeholder="Password ID 4",
            required=False,
            max_length=100
        )

        self.password_5 = discord.ui.TextInput(
            label="Password 5",
            placeholder="Password ID 5",
            required=False,
            max_length=100
        )

        self.add_item(self.password_1)
        self.add_item(self.password_2)
        self.add_item(self.password_3)
        self.add_item(self.password_4)
        self.add_item(self.password_5)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        guild_id = interaction.guild.id

        passwords = {
            1: self.password_1.value,
            2: self.password_2.value,
            3: self.password_3.value,
            4: self.password_4.value,
            5: self.password_5.value
        }

        updated_passwords = {}

        for pass_id, password in passwords.items():

            if not password:
                continue

            result = await update_door_password(
                guild_id=guild_id,
                pass_id=pass_id,
                pass_door=password
            )

            if result is not None:
                updated_passwords[pass_id] = password

        if updated_passwords:

            password_text = "\n".join(
                f"Password {pass_id}: `{password}`"
                for pass_id, password in updated_passwords.items()
            )

            message = (
                f"{len(updated_passwords)} password berhasil diperbarui.\n\n"
                f"{password_text}"
            )

        else:

            message = "Tidak ada password yang diperbarui."

        await interaction.response.send_message(
            message,
            ephemeral=True
        )
# 
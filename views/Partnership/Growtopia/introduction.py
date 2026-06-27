import discord
import traceback


class GTIntroductionModal(discord.ui.Modal, title="Growtopia Introduction"):

    nama = discord.ui.TextInput(
        label="Nama",
        placeholder="Masukkan nama kamu",
        max_length=50
    )

    growid = discord.ui.TextInput(
        label="GrowID",
        placeholder="Masukkan GrowID kamu",
        max_length=30
    )

    async def on_submit(self, interaction: discord.Interaction):

        print("\n========== MODAL SUBMIT ==========")
        print(f"Guild   : {interaction.guild.id}")
        print(f"User    : {interaction.user}")
        print(f"Nama    : {self.nama.value}")
        print(f"GrowID  : {self.growid.value}")
        print("==================================\n")

        try:
            embed = discord.Embed(
                title="📋 Introduction",
                color=discord.Color.green()
            )

            embed.add_field(
                name="Nama",
                value=self.nama.value,
                inline=False
            )

            embed.add_field(
                name="GrowID",
                value=self.growid.value,
                inline=False
            )

            embed.set_footer(
                text=f"Discord : {interaction.user}"
            )

            await interaction.response.send_message(
                embed=embed
            )

        except Exception:
            print("\n========== MODAL ERROR ==========")
            traceback.print_exc()
            print("=================================\n")
            raise


class GTIntroductionView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Isi Introduction",
        emoji="📝",
        style=discord.ButtonStyle.green,
        custom_id="gt:introduction"
    )
    async def introduction(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        print("\n========== BUTTON CLICK ==========")
        print(f"Guild   : {interaction.guild.id}")
        print(f"User    : {interaction.user}")
        print(f"Button  : {button.custom_id}")
        print("==================================\n")

        try:
            await interaction.response.send_modal(
                GTIntroductionModal()
            )

        except Exception:
            print("\n========== BUTTON ERROR ==========")
            traceback.print_exc()
            print("==================================\n")
            raise
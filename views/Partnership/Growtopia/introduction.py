import discord
import traceback

from database.role_manager import get_role_id

ROLE_KEY = "introduction"

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
            
            role_id = await get_role_id(
                interaction.guild.id,
                ROLE_KEY
            )

            if role_id:
                
                role = interaction.guild.get_role(role_id)
                
                if role and role not in interaction.user.roles:

                    try:
                        await interaction.user.add_roles(
                            role,
                            reason="Growtopia Introduction Completed"
                        )

                    except discord.Forbidden:
                        print(
                            f"[GT Intro] Tidak bisa memberikan role {role.name}"
                        )

                    except Exception:
                        traceback.print_exc()
            
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
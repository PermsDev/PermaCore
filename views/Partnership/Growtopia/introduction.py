import discord
import traceback

from database.role_manager import get_role_id
from database.intro_manager import (
    save_user_profile,
    save_intro,
    get_user_profile
)

ROLE_KEY = "introduction"
GAME_KEY = "growtopia"

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
    
    def __init__(
        self,
        nama: str | None = None,
        growid: str | None = None
    ):
        super().__init__()

        if nama:
            self.nama.default = nama

        if growid:
            self.growid.default = growid

    async def on_submit(self, interaction: discord.Interaction):

        print("\n========== MODAL SUBMIT ==========")
        print(f"Guild   : {interaction.guild.id}")
        print(f"User    : {interaction.user}")
        print(f"Nama    : {self.nama.value}")
        print(f"GrowID  : {self.growid.value}")
        print("==================================\n")
        
        try:            
            await save_user_profile(
                guild_id=interaction.guild.id,
                user_id=interaction.user.id,
                nickname=self.nama.value,
                joined_at=interaction.user.joined_at
            )
            
            await save_intro(
                guild_id=interaction.guild.id,
                user_id=interaction.user.id,
                game_key=GAME_KEY,
                value=self.growid.value,
                message_id=None,
                channel_id=None
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
            
            embed = discord.Embed(
                title="✅ Introduction Berhasil",
                description=(
                    "Data introduction kamu berhasil disimpan."
                ),
                color=discord.Color.green()
            )

            embed.add_field(
                name="👤 Nama",
                value=self.nama.value,
                inline=False
            )

            embed.add_field(
                name="🌱 GrowID",
                value=self.growid.value,
                inline=False
            )

            embed.set_footer(
                text=f"Discord ID : {interaction.user.id}"
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
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
            profile = await get_user_profile(
                guild_id=interaction.guild.id,
                user_id=interaction.user.id
            )

            nama = None
            growid = None

            if profile:

                nama = profile.get("nickname")

                games = profile.get("games", {})

                if GAME_KEY in games:
                    growid = games[GAME_KEY]["value"]

            await interaction.response.send_modal(
                GTIntroductionModal(
                    nama=nama,
                    growid=growid
                )
            )

        except Exception:
            print("\n========== BUTTON ERROR ==========")
            traceback.print_exc()
            print("==================================\n")
            raise
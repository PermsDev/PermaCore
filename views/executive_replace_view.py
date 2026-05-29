import discord
from discord.ui import View, Select
# from services.executive_service import refresh_executive_dm

class ReplaceExecutiveSelect(Select):

    def __init__(
        self,
        member: discord.Member,
        role: discord.Role,
        new_nickname: str,
        apply_callback,
        executive_type: str
    ):

        self.member = member
        self.role = role
        self.new_nickname = new_nickname
        self.apply_callback = apply_callback
        self.executive_type = executive_type

        options = [
            discord.SelectOption(
                label="Ya",
                value="yes",
                emoji="✅"
            ),

            discord.SelectOption(
                label="Tidak",
                value="no",
                emoji="❌"
            )
        ]

        super().__init__(
            placeholder="Pilih jawaban...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        # =========================
        # ACK INTERACTION
        # =========================
        await interaction.response.defer()

        # =========================
        # CANCEL
        # =========================
        if self.values[0] == "no":

            await interaction.edit_original_response(
                content="Perubahan dibatalkan.",
                embed=None,
                view=None
            )
            return

        # =========================
        # APPLY EXECUTIVE
        # =========================
        try:

            await self.apply_callback(
                member=self.member,
                role=self.role,
                new_nickname=self.new_nickname
            )

            # lazy import
            from services.executive_service import refresh_executive_dm

            await refresh_executive_dm(
                guild=interaction.guild,
                member=self.member,
                executive_type=self.executive_type,
                role=self.role,
                actor=interaction.user
            )

            embed = discord.Embed(
                title="✅ Executive Updated",
                description=(
                    f"Role executive berhasil diganti "
                    f"menjadi {self.role.mention}\n\n"

                    f"Nickname baru:\n"
                    f"`{self.new_nickname}`"
                ),
                color=discord.Color.green()
            )

            await interaction.edit_original_response(
                content=None,
                embed=embed,
                view=None
            )

        except Exception as e:

            await interaction.edit_original_response(
                content=f"Gagal mengganti executive.\n```{e}```",
                embed=None,
                view=None
            )


class ReplaceExecutiveView(View):

    def __init__(
        self,
        member: discord.Member,
        role: discord.Role,
        new_nickname: str,
        apply_callback,
        executive_type: str
    ):

        super().__init__(timeout=60)

        self.add_item(
            ReplaceExecutiveSelect(
                member=member,
                role=role,
                new_nickname=new_nickname,
                apply_callback=apply_callback,
                executive_type=executive_type
            )
        )
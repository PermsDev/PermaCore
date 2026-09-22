import discord


class TopClashView(discord.ui.View):

    def __init__(
        self,
        growids: list[str],
        user_ids: list[int | None],
        owner_id: int
    ):
        super().__init__(timeout=300)

        self.growids = growids
        self.user_ids = user_ids
        self.owner_id = owner_id

    def get_content(self) -> str:

        lines = [
            "**🏆 Event Clash - Top 5**",
            "",
        ]

        emojis = [
            "🥇",
            "🥈",
            "🥉",
            "4️⃣",
            "5️⃣"
        ]

        for index, (growid, user_id) in enumerate(
            zip(self.growids, self.user_ids)
        ):

            mention = (
                f"<@{user_id}>"
                if user_id
                else "Tidak ditemukan"
            )

            lines.append(
                f"{emojis[index]} Top {index + 1}: "
                f"`{growid}` → {mention}"
            )

        lines.extend([
            "",
            "Silakan periksa data sebelum disimpan."
        ])

        return "\n".join(lines)

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
        label="Edit",
        emoji="✏️",
        style=discord.ButtonStyle.secondary,
        custom_id="guild_manage:top_clash_edit"
    )
    async def edit_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        from views.guild.modals.top_clash import TopClashEditModal

        await interaction.response.send_modal(
            TopClashEditModal(self)
        )

    @discord.ui.button(
        label="Simpan",
        emoji="💾",
        style=discord.ButtonStyle.success,
        custom_id="guild_manage:top_clash_save"
    )
    async def save_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_message(
            "💾 Fitur simpan ke database belum dibuat.",
            ephemeral=True
        )
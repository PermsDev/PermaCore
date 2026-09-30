import discord

from database.core.emoji_manager import get_emoji
from database.guild.door_password_manager import (
    get_door_password_shared_status
)
from database.guild.save_top_clash_manager import save_top_clash
from database.guild.event_clash_score_manager import (
    get_top_monthly_score,
    get_top_total_score
)
from services.guild.league.update_league_panel import update_league_panel
from views.guild.league.embed.send_clash_reward import send_clash_reward


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

        self.shared_status: list[bool | None] = [
            None
        ] * len(growids)

    async def load_shared_status(
        self,
        guild_id: int
    ):

        for index in range(len(self.growids)):

            self.shared_status[index] = (
                await get_door_password_shared_status(
                    guild_id=guild_id,
                    pass_id=index + 1
                )
            )

    def get_content(self) -> str:

        lines = [
            "**🏆 Event Clash - Top 5**",
            "",
        ]

        emojis = [
            get_emoji("medal_1"),
            get_emoji("medal_2"),
            get_emoji("medal_3"),
            get_emoji("medal_4"),
            get_emoji("medal_5")
        ]

        for index, (growid, user_id) in enumerate(
            zip(self.growids, self.user_ids)
        ):

            mention = (
                f"<@{user_id}>"
                if user_id
                else "User tidak ditemukan"
            )

            status = ""

            if self.shared_status[index] is True:
                status = f" {get_emoji('weak_password')}"

            lines.append(
                f"{emojis[index]} Top {index + 1}: "
                f"`{growid}` → {mention}{status}"
            )

        lines.extend([
            "",
            "Silakan periksa data sebelum disimpan. \n"
            f"{get_emoji('weak_password')} → Password belum di perbarui, prize tidak akan di berikan"
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

        from views.guild.guild_manage.modals.top_clash import (
            TopClashEditModal
        )

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

        await interaction.response.defer(
            ephemeral=True
        )

        guild_id = interaction.guild.id

        try:

            result = await save_top_clash(
                growids=self.growids,
                user_ids=self.user_ids
            )

            await update_league_panel(
                guild_id=guild_id
            )

            monthly_scores = await get_top_monthly_score(
                series_id=result["series_id"]
            )

            total_scores = await get_top_total_score(
                series_id=result["series_id"]
            )

        except Exception as error:

            print(
                f"[Event Clash] Gagal menyimpan: {error}"
            )

            await interaction.followup.send(
                "❌ Terjadi kesalahan saat menyimpan "
                "hasil Event Clash.",
                ephemeral=True
            )

            return

        for child in self.children:
            child.disabled = True

        for index, user_id in enumerate(self.user_ids):

            if user_id is None:
                continue

            user = interaction.guild.get_member(user_id)

            if user is None:
                continue

            pass_id = index + 1

            is_shared = await get_door_password_shared_status(
                guild_id=guild_id,
                pass_id=pass_id
            )

            if is_shared is True:

                print(
                    f"[Event Clash] Door password {pass_id} "
                    f"sudah diberikan. DM dilewati."
                )

                continue

            growid = self.growids[index]

            monthly_data = next(
                (
                    row
                    for row in monthly_scores
                    if row["user_id"] == user_id
                ),
                None
            )

            total_data = next(
                (
                    row
                    for row in total_scores
                    if row["user_id"] == user_id
                ),
                None
            )

            if monthly_data is None:

                print(
                    f"[Event Clash] Monthly score "
                    f"user {user_id} tidak ditemukan."
                )

                continue

            if total_data is None:

                print(
                    f"[Event Clash] Total score "
                    f"user {user_id} tidak ditemukan."
                )

                continue

            monthly_rank = (
                monthly_scores.index(monthly_data) + 1
            )

            total_rank = (
                total_scores.index(total_data) + 1
            )

            monthly_points = monthly_data["points"]
            total_points = total_data["total_points"]

            try:

                await send_clash_reward(
                    user=user,
                    guild_id=guild_id,
                    pass_id=pass_id,
                    growid=growid,
                    monthly_rank=monthly_rank,
                    monthly_points=monthly_points,
                    total_rank=total_rank,
                    total_points=total_points
                )

            except discord.Forbidden:

                print(
                    f"[Event Clash] DM tidak dapat dikirim "
                    f"ke {user}."
                )

            except discord.HTTPException as error:

                print(
                    f"[Event Clash] Gagal mengirim DM "
                    f"ke {user}: {error}"
                )

        await interaction.edit_original_response(
            content=(
                "✅ **Event Clash berhasil disimpan.**\n\n"
                f"Series: `{result['series_name']}`\n"
                f"Tanggal: `{result['event_date']}`"
            ),
            view=self
        )
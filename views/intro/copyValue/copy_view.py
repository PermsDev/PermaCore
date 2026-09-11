import discord

from database.core.intro_manager import get_user_intro


class CopyButton(discord.ui.Button):

    def __init__(
        self,
        game_key: str,
        user_id: str
    ):
        super().__init__(
            label="Copy ID",
            style=discord.ButtonStyle.secondary,
            emoji="📋",
            custom_id=f"copy:{game_key}:{user_id}"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        parts = self.custom_id.split(":")

        if len(parts) != 3:
            await interaction.response.send_message(
                "❌ Invalid button data.",
                ephemeral=True
            )
            return

        _, game_key, target_user_id = parts

        # =========================
        # GET INTRO DATA
        # =========================

        intro_data = await get_user_intro(
            int(target_user_id)
        )

        # =========================
        # FIND GAME DATA
        # =========================

        game_data = next(
            (
                intro
                for intro in intro_data
                if intro["game_key"] == game_key
            ),
            None
        )

        if not game_data or not game_data.get("value"):

            await interaction.response.send_message(
                "❌ Data tidak ditemukan.",
                ephemeral=True
            )

            return

        value = game_data["value"]

        # =========================
        # GAME NAME
        # =========================

        game_names = {
            "mlbb": "Mobile Legends ID",
            "roblox": "Roblox Username"
        }

        # =========================
        # EMBED
        # =========================

        embed = discord.Embed(
            title=game_names.get(
                game_key,
                game_key
            ),
            description=value,
            color=discord.Color.blurple()
        )

        embed.set_footer(
            text="Klik kanan / tekan lama untuk copy"
        )

        # =========================
        # RESPONSE
        # =========================

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


class CopyView(discord.ui.View):

    def __init__(
        self,
        game_key: str,
        user_id: str
    ):
        super().__init__(
            timeout=None
        )

        self.add_item(
            CopyButton(
                game_key,
                user_id
            )
        )
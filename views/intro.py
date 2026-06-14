import discord
import asyncio
from services.card_generator import generate_card, get_avatar

from utils.logger import send_log
from utils.validate import validate_growid, validate_pw, validate_roblox, validate_mlbb

from database.role_manager import get_roles, get_no_rename_roles
from database.channel_manager import get_game_channels
from database.intro_manager import (
    get_user_profile,
    save_intro,
    delete_intro,
    save_user_profile,
    get_copyview_intros
)

GAME_BACKGROUNDS = {
    "growtopia": "bg_gt.png",
    "pw": "bg_pw.png",
    "mlbb": "bg_mlbb.png",
    "roblox": "bg_roblox.png",
}
            
# ======================
# PERSISTENT COPY VIEW
# ======================
class CopyButton(discord.ui.Button):
    def __init__(self, game_key: str, user_id: str):
        super().__init__(
            label="Copy ID",
            style=discord.ButtonStyle.secondary,
            emoji="📋",
            custom_id=f"copy:{game_key}:{user_id}"
        )

    async def callback(self, interaction: discord.Interaction):
        parts = self.custom_id.split(":")

        if len(parts) != 3:
            await interaction.response.send_message(
                "❌ Invalid button data.",
                ephemeral=True
            )
            return

        _, game_key, target_user_id = parts

        guild_id = interaction.guild.id

        user_data = get_user_profile(int(guild_id), int(target_user_id))

        game_data = user_data.get("games", {}).get(game_key, {})
        value = game_data.get("value")

        if not value:
            await interaction.response.send_message(
                "❌ Data tidak ditemukan.",
                ephemeral=True
            )
            return
        
        game_names = {
            "mlbb": "Mobile Legends ID",
            "roblox": "Roblox Username"
        }

        embed = discord.Embed(
            title=game_names.get(game_key, game_key),
            description=f"{value}",
            color=discord.Color.blurple()
        )
        embed.set_footer(
            text="Klik kanan / tekan lama untuk copy"
        )
        
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

class CopyView(discord.ui.View):
    def __init__(self, game_key: str, user_id: str):
        super().__init__(timeout=None)
        self.add_item(
            CopyButton(game_key, user_id)
        )
# ======================
# MODAL
# ======================
class IntroModal(discord.ui.Modal):
    def __init__(self, user_data=None):
        super().__init__(title="Intro Profile")
        
        # ambil data lama kalau ada
        user_data = user_data or {}
        
        # ======================
        # FIELD
        # ======================
        self.nickname = discord.ui.TextInput(
            label="Nama Panggilan",
            required=True,
            max_length=32,
            default=user_data.get("nickname", "")
        )
        
        self.growtopia = discord.ui.TextInput(
            label="Growtopia (GrowID)",
            required=False,
            max_length=20,
            default=user_data.get("games", {}).get("growtopia", {}).get("value", "")
        )
        
        self.pw = discord.ui.TextInput(
            label="Pixel World (Username)",
            required=False,
            max_length=20,
            default=user_data.get("games", {}).get("pw", {}).get("value", "")
        )
        
        self.mlbb = discord.ui.TextInput(
            label="Mobile Legends (ID)",
            required=False,
            max_length=20,
            default=user_data.get("games", {}).get("mlbb", {}).get("value", "")
        )
        
        self.roblox = discord.ui.TextInput(
            label="Roblox (Username)",
            required=False,
            max_length=20,
            default=user_data.get("games", {}).get("roblox", {}).get("value", "")
        )

        # tambahkan ke modal
        self.add_item(self.nickname)
        self.add_item(self.growtopia)
        self.add_item(self.pw)
        self.add_item(self.mlbb)
        self.add_item(self.roblox)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        guild_id = interaction.guild.id
        user_id = interaction.user.id
        
        roles = get_roles(
            int(guild_id)
        ) or {}

        # VERIFIED_INTRODUCTION_ID = roles["role_key"].get("verified_intro")
        VERIFIED_INTRODUCTION_ID = (
            roles.get("by_group", {})
            .get("verified", {})
            .get("verified_intro")
        )

        NO_RENAME_ROLES = (
            get_no_rename_roles(
                int(guild_id)
            ) or []
        )
        
        # ======================
        # DATA LAMA
        # ======================
        old_user_data = get_user_profile(
            interaction.guild.id,
            interaction.user.id
        ) or {}
        
        # ======================
        # VALIDASI GAME
        # ======================
        
        growtopia_valid, growtopia_error = validate_growid(
            self.growtopia.value.strip()
        )
        
        pw_valid, pw_error = validate_pw(
            self.pw.value.strip()
        )
        
        roblox_valid, roblox_error = validate_roblox(
            self.roblox.value.strip()
        )
        
        mlbb_valid, mlbb_error = validate_mlbb(
            self.mlbb.value.strip()
        )

        # ======================
        # RENAME USER
        # ======================
        rename_success = True
        blocked_rename = False

        try:

            member_roles = [role.id for role in interaction.user.roles]

            blocked_rename = any(
                role_id in NO_RENAME_ROLES
                for role_id in member_roles
            )

            new_nick = self.nickname.value.strip()
            
            # ======================
            # APPLY NICKNAME
            # ======================
            if not blocked_rename:
                await interaction.user.edit(
                    nick=new_nick
                )

        except discord.Forbidden:
            rename_success = False
            
        # ======================
        # DATA LAMA
        # ======================
        old_nickname = (old_user_data.get("nickname") or "").strip()
        new_nickname = (self.nickname.value or "").strip()

        nickname_changed = old_nickname != new_nickname

        # ======================
        # GAME FIELD
        # ======================
        game_fields = {
            "growtopia": self.growtopia.value.strip(),
            "pw": self.pw.value.strip(),
            "mlbb": self.mlbb.value.strip(),
            "roblox": self.roblox.value.strip()
        }
        
        # ======================
        # DOWNLOAD AVATAR SEKALI
        # ======================
        avatar = await get_avatar(
            str(interaction.user.display_avatar.url)
        )

        send_tasks = []
        pending_games = []

        successful_games = []
        input_warnings = []
        failed_games = []
        removed_games = []
        save_success = False

        # ======================
        # LOOP GAME
        # ======================
        for game_key, game_value in game_fields.items():

            old_game_data = (
                old_user_data
                .get("games", {})
                .get(game_key, {})
            )

            old_value = old_game_data.get("value", "").strip()
            new_value = game_value.strip()
            
            if game_key == "growtopia" and not growtopia_valid:
                input_warnings.append({
                    "game": "growtopia",
                    "error": growtopia_error
                })

                if nickname_changed and old_value:
                    new_value = old_value
                else:
                    continue

            if game_key == "pw" and not pw_valid:
                input_warnings.append({
                    "game": "pw",
                    "error": pw_error
                })
                if nickname_changed and old_value:
                    new_value = old_value
                else:
                    continue

            if game_key == "roblox" and not roblox_valid:
                
                input_warnings.append({
                    "game": "roblox",
                    "error": roblox_error
                })
                
                if nickname_changed and old_value:
                    new_value = old_value
                else:
                    continue
            
            if game_key == "mlbb" and not mlbb_valid:
                input_warnings.append({
                    "game": "mlbb",
                    "error": mlbb_error
                })
                # ADD LOG WARNING
                await send_log(
                    guild=interaction.guild,
                    log_type="WARNING",
                    action="Introduction",
                    emoji="⚠️",
                    user=interaction.user,
                    details={
                        "Game": "Mobile Legends",
                        "Error": mlbb_error
                    }
                )
                if nickname_changed and old_value:
                    new_value = old_value
                else:
                    continue

            # skip kalau tidak berubah
            if old_value == new_value and not nickname_changed:
                continue

            GAME_CHANNELS = get_game_channels(interaction.guild.id)

            channel_id = GAME_CHANNELS.get(game_key)

            if not channel_id:
                continue

            channel = interaction.guild.get_channel(channel_id)

            if not channel:
                continue

            old_message_id = old_game_data.get("message_id")

            # ======================
            # FIELD DIKOSONGKAN
            # ======================
            if not new_value:

                if old_value:

                    removed_games.append(game_key)

                    old_message_id = old_game_data.get("message_id")

                    if old_message_id:

                        try:

                            old_msg = await channel.fetch_message(
                                old_message_id
                            )

                            await old_msg.delete()
                            delete_intro(
                                interaction.guild.id,
                                interaction.user.id,
                                game_key
                            )

                        except discord.NotFound:
                            delete_intro(
                                interaction.guild.id,
                                interaction.user.id,
                                game_key
                            )

                        except discord.Forbidden:
                            await send_log(
                                guild=interaction.guild,
                                log_type="WARNING",
                                action="Delete Introduction",
                                emoji="⚠️",
                                user=interaction.user,
                                details={
                                    "Game": game_key,
                                    "Message ID": old_message_id,
                                    "Reason": "Missing permissions"
                                }
                            )

                        except Exception as e:

                            await send_log(
                                guild=interaction.guild,
                                log_type="WARNING",
                                action="Delete Introduction",
                                emoji="⚠️",
                                user=interaction.user,
                                details={
                                    "Game": game_key,
                                    "Message ID": old_message_id,
                                    "Error": str(e)
                                }
                            )
                continue

            # ======================
            # GENERATE CARD
            # ======================
            buffer = await generate_card(
                user=interaction.user,
                avatar=avatar,
                game_text=new_value,
                background_name=GAME_BACKGROUNDS[game_key],
                display_name=self.nickname.value,
                joined_at=interaction.user.joined_at.isoformat()
            )

            file = discord.File(
                fp=buffer,
                filename=f"{game_key}.png"
            )

            view = None

            if game_key in ["mlbb", "roblox"]:
                view = CopyView(game_key, user_id)

            send_tasks.append(
                channel.send(
                    content=f"📢 Member {interaction.user.mention} telah memperkenalkan diri!",
                    file=file,
                    view=view
                )
            )

            pending_games.append({
                "game_key": game_key,
                "value": new_value,
                "channel_id": channel.id,
                "old_message_id": old_message_id
            })

        # ======================
        # SEND ALL MESSAGE
        # ======================
        messages = await asyncio.gather(
            *send_tasks,
            return_exceptions=True
        )

        # ======================
        # PREPARE MESSAGE DATA
        # ======================
        message_results = {}

        for i, message in enumerate(messages):

            game_data = pending_games[i]
            game_key = game_data["game_key"]
            
            # ======================
            # JIKA ERROR
            # ======================
            if isinstance(message, Exception):

                failed_games.append({
                    "game": game_key,
                    "error": str(message)
                })
                await send_log(
                    guild=interaction.guild,
                    log_type="ERROR",
                    action="Send Introduction Card",
                    emoji="❌",
                    user=interaction.user,
                    details={
                        "Game": game_key,
                        "Error": str(message)
                    }
                )
                continue

            # ======================
            # SUCCESS
            # ======================
            successful_games.append(game_key)

            message_results[game_key] = {
                "value": game_data["value"],
                "message_id": message.id,
                "channel_id": game_data["channel_id"]
            }

            # ======================
            # DELETE OLD MESSAGE
            # ======================
            old_message_id = game_data.get("old_message_id")

            if old_message_id:

                try:

                    channel = interaction.guild.get_channel(
                        game_data["channel_id"]
                    )

                    if channel:

                        old_msg = await channel.fetch_message(
                            old_message_id
                        )

                        await old_msg.delete()

                except discord.NotFound:
                    pass

                except discord.Forbidden:

                    await send_log(
                        guild=interaction.guild,
                        log_type="WARNING",
                        action="Delete Old Introduction",
                        emoji="⚠️",
                        user=interaction.user,
                        details={
                            "Game": game_key,
                            "Message ID": old_message_id,
                            "Reason": "Missing permissions"
                        }
                    )

                except Exception as e:

                    await send_log(
                        guild=interaction.guild,
                        log_type="WARNING",
                        action="Delete Old Introduction",
                        emoji="⚠️",
                        user=interaction.user,
                        details={
                            "Game": game_key,
                            "Message ID": old_message_id,
                            "Error": str(e)
                        }
                    )
        # ======================
        # SAVE DATA
        # ======================

        try:

            save_user_profile(
                guild_id=interaction.guild.id,
                user_id=interaction.user.id,
                nickname=self.nickname.value.strip(),
                joined_at=interaction.user.joined_at
            )

            for game_key, data in message_results.items():

                save_intro(
                    guild_id=interaction.guild.id,
                    user_id=interaction.user.id,
                    game_key=game_key,
                    value=data["value"],
                    message_id=data["message_id"],
                    channel_id=data["channel_id"]
                )

            save_success = True

        except Exception as e:

            save_success = False
            save_error = str(e)

        # ======================
        # RESPONSE MESSAGE
        # ======================
        response_text = ""
        nickname_info = ""
        
        if blocked_rename:
            nickname_info = (
                "\n🔒 Nickname tidak diubah karena "
                "memiliki role yang dilindungi."
            )
            
        else:
            nickname_info = (
                f"\n📝 Nickname diset menjadi "
                f"`{self.nickname.value.strip()}`"
            )

        # ======================
        # RENAME STATUS
        # ======================
        if rename_success:
            response_text += (
                "✅ Pengenalan berhasil dibuat!\n"
            )
            response_text += nickname_info

        else:
            response_text += (
                "⚠️ Nickname tidak bisa diubah "
                "(role anda lebih tinggi), "
                "tapi data tetap tersimpan."
            )

        pretty_names = {
            "growtopia": "Growtopia",
            "pw": "Pixel World",
            "mlbb": "Mobile Legends",
            "roblox": "Roblox"
        }
        # ======================
        # GAME SUCCESS
        # ======================
        if successful_games:

            success_list = [
                pretty_names.get(game, game)
                for game in successful_games
            ]

            response_text += (
                "\n\n✅ Profile berhasil dibuat:"
                f"\n• " + "\n• ".join(success_list)
            )

        # ======================
        # GAME FAILED
        # ======================
        if failed_games:

            response_text += "\n\n❌ Profile gagal dibuat:"

            for failed in failed_games:

                game_name = pretty_names.get(
                    failed["game"],
                    failed["game"]
                )

                response_text += (
                    f"\n• {game_name} — {failed['error']}"
                )
                
        # ======================
        # INPUT WARNINGS
        # ======================
        if input_warnings:

            response_text += "\n\n⚠️ Input tidak valid, data lama tetap digunakan:"

            for warning in input_warnings:

                game_name = pretty_names.get(
                    warning["game"],
                    warning["game"]
                )

                response_text += (
                    f"\n• {game_name} — {warning['error']}"
                )
            
        # ======================
        # SAVE STATUS
        # ======================
        if not save_success:

            response_text += (
                "\n\n❌ Data gagal disimpan:"
                f"\n`{save_error}`"
            )
        
        # ======================
        # GIVE VERIFIED ROLE
        # ======================
        if save_success:
            verified_intro = interaction.guild.get_role(
                VERIFIED_INTRODUCTION_ID
            )
            if verified_intro:
                try:
                    if verified_intro not in interaction.user.roles:
                        await interaction.user.add_roles(
                            verified_intro,
                            reason="User completed intro"
                        )
                except discord.Forbidden:
                    pass
                except discord.HTTPException:
                    pass

        # ======================
        # SEND RESPONSE
        # ======================
        await interaction.followup.send(
            response_text,
            ephemeral=True
        )

        # ======================
        # SUCCESS LOG
        # ======================
        await send_log(
            guild=interaction.guild,
            log_type="SUCCESS",
            action="Introduction",
            emoji="📝",
            user=interaction.user,
            details={
                "Rename Success": rename_success,
                "Successful Games": (
                    ", ".join(successful_games)
                    if successful_games
                    else "Tidak ada"
                ),
                "Removed Games": (
                    ", ".join(removed_games)
                    if removed_games
                    else "Tidak ada"
                ),
                "Failed Games": (
                    ", ".join(
                        [
                            failed["game"]
                            for failed in failed_games
                        ]
                    )
                    if failed_games
                    else "Tidak ada"
                ),
            }
        )
        
# ======================
# BUTTON VIEW
# ======================
class IntroButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Isi Intro", style=discord.ButtonStyle.green, custom_id="intro_button")
    async def intro_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        guild_id = interaction.guild.id
        user_id = interaction.user.id

        user_data = get_user_profile(
            guild_id,
            user_id
        )

        await interaction.response.send_modal(IntroModal(user_data))

# ======================
# REGISTER COPY VIEWS
# ======================
async def register_persistent_views(bot):

    intros = get_copyview_intros()

    for intro in intros:

        bot.add_view(
            CopyView(
                intro["game_key"],
                str(intro["user_id"])
            )
        )
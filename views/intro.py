from services.card_generator import (
    generate_card,
    get_avatar
)
from utils.logger import send_log
from dotenv import load_dotenv
import discord
# import json
import os
import asyncio

from utils.json_manager import (
    INTRO_DATA_PATH,
    load_json,
    update_json
)

from utils.validate import(
    validate_growid, validate_pw, validate_roblox, validate_mlbb
)

load_dotenv()
# role special
EXECUTIVE_GUILD_ROLE_ID = int(os.getenv("EXECUTIVE_GUILD_ROLE_ID", 0))
EXECUTIVE_CLAN_ROLE_ID = int(os.getenv("EXECUTIVE_CLAN_ROLE_ID", 0))
VERIFIED_ROLE_ID = int(os.getenv("VERIFIED_ROLE_ID", 0))
NO_RENAME_ROLES = { 1030431425784188948, 1030432479246553141 }

GAME_CHANNELS = {
    "growtopia": int(os.getenv("GT_CHANNEL", 0)),
    "pw": int(os.getenv("PW_CHANNEL", 0)),
    "mlbb": int(os.getenv("MLBB_CHANNEL", 0)),
    "roblox": int(os.getenv("ROBLOX_CHANNEL", 0)),
}

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

        data = await load_json(INTRO_DATA_PATH)

        guild_id = str(interaction.guild.id)

        user_data = (
            data
            .get(guild_id, {})
            .get(target_user_id, {})
        )

        game_data = (
            user_data
            .get("games", {})
            .get(game_key, {})
        )

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
        
        data = await load_json(INTRO_DATA_PATH)

        
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        
        # ======================
        # DATA LAMA
        # ======================
        old_user_data = (
            data
            .get(guild_id, {})
            .get(user_id, {})
        )
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

        try:

            member_roles = [role.id for role in interaction.user.roles]

            blocked_rename = any(
                role_id in NO_RENAME_ROLES
                for role_id in member_roles
            )

            old_games = old_user_data.get(
                "games",
                {}
            )

            # ======================
            # EFFECTIVE VALUE
            # ======================
            effective_gt = (
                self.growtopia.value.strip()
                if (
                    growtopia_valid
                    and self.growtopia.value.strip()
                )
                else old_games.get(
                    "growtopia",
                    {}
                ).get(
                    "value",
                    ""
                )
            )

            effective_pw = (
                self.pw.value.strip()
                if (
                    pw_valid
                    and self.pw.value.strip()
                )
                else old_games.get(
                    "pw",
                    {}
                ).get(
                    "value",
                    ""
                )
            )

            new_nick = self.nickname.value.strip()

            # ======================
            # PRIORITAS ROLE GT
            # ======================
            if (
                EXECUTIVE_GUILD_ROLE_ID
                in member_roles
                and effective_gt
            ):
                new_nick = (
                    f"{effective_gt} ❄️"
                )

            # ======================
            # ROLE PIXEL WORLD
            # ======================
            elif (
                EXECUTIVE_CLAN_ROLE_ID
                in member_roles
                and effective_pw
            ):
                new_nick = (
                    f"{effective_pw} 🔆"
                )

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
        old_nickname = old_user_data.get("nickname", "").strip()
        new_nickname = self.nickname.value.strip()

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

                        except discord.NotFound:
                            pass

                        except discord.Forbidden:
                            pass

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
        def updater(data):
            validation_status = {
                "growtopia": growtopia_valid,
                "pw": pw_valid,
                "mlbb": mlbb_valid,
                "roblox": roblox_valid
            }

            if guild_id not in data:
                data[guild_id] = {}

            new_games = {}

            for game_key, game_value in game_fields.items():

                clean_value = game_value.strip()

                if not validation_status[game_key]:

                    old_game = (
                        data
                        .get(guild_id, {})
                        .get(user_id, {})
                        .get("games", {})
                        .get(game_key)
                    )

                    if old_game:
                        new_games[game_key] = old_game

                    continue

                # kalau kosong jangan disimpan
                if not clean_value:
                    continue

                # kalau ada message result baru
                if game_key in message_results:
                    new_games[game_key] = message_results[game_key]

                else:
                    # kalau tidak berubah ambil data lama
                    old_game = (
                        data
                        .get(guild_id, {})
                        .get(user_id, {})
                        .get("games", {})
                        .get(game_key)
                    )

                    if old_game:
                        new_games[game_key] = old_game

            data[guild_id][user_id] = {
                "nickname": self.nickname.value,
                "joined_at": interaction.user.joined_at.isoformat(),
                "games": new_games
            }

        try:
            await update_json(INTRO_DATA_PATH, updater)
            save_success = True
        except Exception as e:
            save_success = False
            save_error = str(e)
            
            # ADD LOG ERROR
            await send_log(
                guild=interaction.guild,
                log_type="ERROR",
                action="Save Introduction",
                emoji="❌",
                user=interaction.user,
                details={
                    "Error": str(e)
                }
            )

        # ======================
        # RESPONSE MESSAGE
        # ======================
        response_text = ""
        nickname_info = ""

        # ======================
        # NICKNAME INFO
        # ======================
        if (
            EXECUTIVE_GUILD_ROLE_ID in member_roles
            and effective_gt
        ):
            nickname_info = (
                f"\n❄️ Nickname disesuaikan menjadi "
                f"`{effective_gt} ❄️`"
            )

        elif (
            EXECUTIVE_CLAN_ROLE_ID in member_roles
            and effective_pw
        ):
            nickname_info = (
                f"\n🔆 Nickname disesuaikan menjadi "
                f"`{effective_pw} 🔆`"
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
                "(role lebih tinggi), "
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
            
        #     response_text += (
        #         "\n\n💾 Data berhasil disimpan."
        #     )

        # else:

            
        
        # ======================
        # GIVE VERIFIED ROLE
        # ======================
        if save_success:
            verified_role = interaction.guild.get_role(
                VERIFIED_ROLE_ID
            )
            if verified_role:
                try:
                    if verified_role not in interaction.user.roles:
                        await interaction.user.add_roles(
                            verified_role,
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
        # from views.intro import IntroModal, load_json

        data = await load_json(INTRO_DATA_PATH)
        
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)

        user_data = data.get(guild_id, {}).get(user_id)

        await interaction.response.send_modal(IntroModal(user_data))

# ======================
# REGISTER COPY VIEWS
# ======================
async def register_persistent_views(bot):

    data = await load_json(INTRO_DATA_PATH)

    for guild_id, guild_data in data.items():

        for user_id, user_data in guild_data.items():

            games = user_data.get("games", {})

            for game_key in ["mlbb", "roblox"]:

                game_data = games.get(game_key)

                if not game_data:
                    continue

                if not game_data.get("message_id"):
                    continue

                bot.add_view(
                    CopyView(game_key, user_id)
                )
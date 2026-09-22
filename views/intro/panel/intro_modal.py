import discord
import asyncio

from services.card_generator import generate_card, get_avatar

from services.display_name.update_display_name import update_display_name

from utils.logger import send_log
from utils.validate import validate_growid, validate_roblox, validate_mlbb

from database.core.role_manager import get_roles
from database.core.channel_manager import get_game_channels
from database.core.intro_manager import (
    get_user_profile,
    save_intro,
    delete_intro,
    save_user_profile
)

from database.main.user.display_name_manager import (
    get_or_create_display_source,
    set_display_source
)

from views.intro.copyValue.copy_view import CopyView


GAME_BACKGROUNDS = {
    "growtopia": "bg_gt.png",
    "mlbb": "bg_mlbb.png",
    "roblox": "bg_roblox.png",
}

pretty_names = {
    "growtopia": "Growtopia",
    "mlbb": "Mobile Legends",
    "roblox": "Roblox"
}

# ======================
# MODAL
# ======================
class IntroModal(discord.ui.Modal):

    def __init__(self, user_data=None):

        super().__init__(
            title="Intro Profile"
        )

        # ======================
        # DATA LAMA
        # ======================

        user_data = user_data or {}

        # ======================
        # FIELD
        # ======================

        self.nickname = discord.ui.TextInput(
            label="Nama Panggilan",
            required=True,
            max_length=32,
            default=user_data.get(
                "nickname",
                ""
            )
        )

        self.growtopia = discord.ui.TextInput(
            label="Growtopia (GrowID)",
            required=False,
            max_length=20,
            default=user_data.get(
                "games",
                {}
            ).get(
                "growtopia",
                {}
            ).get(
                "value",
                ""
            )
        )

        self.mlbb = discord.ui.TextInput(
            label="Mobile Legends (ID)",
            required=False,
            max_length=20,
            default=user_data.get(
                "games",
                {}
            ).get(
                "mlbb",
                {}
            ).get(
                "value",
                ""
            )
        )

        self.roblox = discord.ui.TextInput(
            label="Roblox (Username)",
            required=False,
            max_length=20,
            default=user_data.get(
                "games",
                {}
            ).get(
                "roblox",
                {}
            ).get(
                "value",
                ""
            )
        )

        # ======================
        # ADD FIELD
        # ======================

        self.add_item(self.nickname)
        self.add_item(self.growtopia)
        self.add_item(self.mlbb)
        self.add_item(self.roblox)


    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.defer(
            ephemeral=True
        )

        guild_id = interaction.guild.id
        user_id = interaction.user.id

        # ======================
        # ROLES
        # ======================

        roles = await get_roles(
            int(guild_id)
        ) or {}

        RESIDENTS_ROLE_ID = (
            roles.get("by_group", {})
            .get("pangkat", {})
            .get("residents")
        )

        # ======================
        # DATA LAMA
        # ======================

        old_user_data = await get_user_profile(
            guild_id,
            user_id
        ) or {}

        # ======================
        # FIRST INTRO CHECK
        # ======================

        is_first_intro = not bool(
            old_user_data
        )

        # ======================
        # FIRST INTRO
        # DEFAULT DISPLAY SOURCE
        # ======================

        if is_first_intro:

            await set_display_source(
                guild_id=guild_id,
                user_id=user_id,
                display_source="nickname"
            )

        # ======================
        # VALIDASI GAME
        # ======================

        growtopia_valid, growtopia_error = validate_growid(
            self.growtopia.value.strip()
        )

        roblox_valid, roblox_error = validate_roblox(
            self.roblox.value.strip()
        )

        mlbb_valid, mlbb_error = validate_mlbb(
            self.mlbb.value.strip()
        )

        # ======================
        # DATA LAMA
        # ======================

        old_nickname = (
            old_user_data
            .get("nickname") or ""
        ).strip()

        new_nickname = (
            self.nickname.value or ""
        ).strip()

        nickname_changed = (
            old_nickname != new_nickname
        )

        # ======================
        # GAME FIELD
        # ======================

        game_fields = {
            "growtopia": self.growtopia.value.strip(),
            "mlbb": self.mlbb.value.strip(),
            "roblox": self.roblox.value.strip()
        }

        # ======================
        # DOWNLOAD AVATAR SEKALI
        # ======================

        avatar = await get_avatar(
            str(
                interaction.user.display_avatar.url
            )
        )

        send_tasks = []
        pending_games = []

        successful_games = []
        display_source_warnings = []
        input_warnings = []
        failed_games = []
        removed_games = []

        save_success = False
        save_error = None

        # ======================
        # GAME CHANNELS
        # ======================

        GAME_CHANNELS = await get_game_channels(
            guild_id
        )

        # ======================
        # LOOP GAME
        # ======================

        for game_key, game_value in game_fields.items():

            old_game_data = (
                old_user_data
                .get("games", {})
                .get(game_key, {})
            )

            old_value = (
                old_game_data
                .get("value", "")
                .strip()
            )

            new_value = game_value.strip()

            # ======================
            # GROWTOPIA VALIDATION
            # ======================

            if (
                game_key == "growtopia"
                and not growtopia_valid
            ):

                input_warnings.append({
                    "game": "growtopia",
                    "error": growtopia_error
                })

                if nickname_changed and old_value:
                    new_value = old_value
                else:
                    continue

            # ======================
            # ROBLOX VALIDATION
            # ======================

            if (
                game_key == "roblox"
                and not roblox_valid
            ):

                input_warnings.append({
                    "game": "roblox",
                    "error": roblox_error
                })

                if nickname_changed and old_value:
                    new_value = old_value
                else:
                    continue

            # ======================
            # MLBB VALIDATION
            # ======================

            if (
                game_key == "mlbb"
                and not mlbb_valid
            ):

                input_warnings.append({
                    "game": "mlbb",
                    "error": mlbb_error
                })

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

            # ======================
            # SKIP JIKA TIDAK BERUBAH
            # ======================

            if (
                old_value == new_value
                and not nickname_changed
            ):
                continue

            channel_id = GAME_CHANNELS.get(
                game_key
            )

            if not channel_id:
                continue

            channel = interaction.guild.get_channel(
                channel_id
            )

            if not channel:
                continue

            old_message_id = old_game_data.get(
                "message_id"
            )

            # ======================
            # FIELD DIKOSONGKAN
            # ======================

            if not new_value:

                if old_value:

                    removed_games.append(
                        game_key
                    )

                    # ======================
                    # CEK DISPLAY SOURCE
                    # ======================

                    display_source_map = {
                        "growtopia": "growid",
                        "roblox": "roblox"
                    }

                    display_source = await get_or_create_display_source(
                        guild_id,
                        user_id
                    )

                    if display_source == display_source_map.get(game_key):

                        display_source_warnings.append(
                            game_key
                        )

                        continue

                    # ======================
                    # HAPUS CARD
                    # ======================

                    if old_message_id:

                        try:

                            old_msg = await channel.fetch_message(
                                old_message_id
                            )

                            await old_msg.delete()

                            await delete_intro(
                                guild_id,
                                user_id,
                                game_key
                            )

                        except discord.NotFound:

                            await delete_intro(
                                guild_id,
                                user_id,
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
                background_name=GAME_BACKGROUNDS[
                    game_key
                ],
                display_name=self.nickname.value,
                joined_at=interaction.user.joined_at.isoformat()
            )

            file = discord.File(
                fp=buffer,
                filename=f"{game_key}.png"
            )

            view = None

            if game_key in [
                "mlbb",
                "roblox"
            ]:

                view = CopyView(
                    game_key,
                    user_id
                )

            send_tasks.append(
                channel.send(
                    content=(
                        f"📢 Member "
                        f"{interaction.user.mention} "
                        f"telah memperkenalkan diri!"
                    ),
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
            # ERROR
            # ======================

            if isinstance(
                message,
                Exception
            ):

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

            successful_games.append(
                game_key
            )

            message_results[game_key] = {
                "value": game_data["value"],
                "message_id": message.id,
                "channel_id": game_data["channel_id"]
            }

            # ======================
            # DELETE OLD MESSAGE
            # ======================

            old_message_id = game_data.get(
                "old_message_id"
            )

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

            # ======================
            # SAVE USER PROFILE
            # ======================

            await save_user_profile(
                guild_id=guild_id,
                user_id=user_id,
                nickname=self.nickname.value.strip(),
                joined_at=interaction.user.joined_at
            )

            # ======================
            # SAVE INTRO
            # ======================

            for game_key, data in message_results.items():

                await save_intro(
                    guild_id=guild_id,
                    user_id=user_id,
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
        # RENAME DISCORD
        # ======================
        rename_success = False

        if save_success:

            rename_success = await update_display_name(
                interaction.user
            )

        # ======================
        # RESPONSE MESSAGE
        # ======================

        response_text = ""

        if rename_success:

            response_text += (
                "✅ Pengenalan berhasil dibuat!\n"
                f"📝 Display name diset menjadi {interaction.user.mention}"
            )
        else:
            response_text += (
                "\n⚠️ Display name tidak bisa diubah "
                "(role bot lebih rendah), "
                "tapi data tetap tersimpan."
            )
            
        # ======================
        # DISPLAY SOURCE WARNINGS
        # ======================

        if display_source_warnings:

            response_text += (
                "\n\n⚠️ Profile game tidak dihapus:"
            )

            for game in display_source_warnings:

                game_name = pretty_names.get(
                    game,
                    game
                )

                response_text += (
                    f"\n• {game_name} sedang digunakan "
                    "sebagai display name."
                )

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
                f"\n• "
                + "\n• ".join(success_list)
            )

        # ======================
        # GAME FAILED
        # ======================

        if failed_games:

            response_text += (
                "\n\n❌ Profile gagal dibuat:"
            )

            for failed in failed_games:

                game_name = pretty_names.get(
                    failed["game"],
                    failed["game"]
                )

                response_text += (
                    f"\n• {game_name} — "
                    f"{failed['error']}"
                )

        # ======================
        # INPUT WARNINGS
        # ======================

        if input_warnings:

            response_text += (
                "\n\n⚠️ Input tidak valid, "
                "data lama tetap digunakan:"
            )

            for warning in input_warnings:

                game_name = pretty_names.get(
                    warning["game"],
                    warning["game"]
                )

                response_text += (
                    f"\n• {game_name} — "
                    f"{warning['error']}"
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
        # GIVE RESIDENTS ROLE
        # ======================

        if save_success:
            
            residents_role = interaction.guild.get_role(
                RESIDENTS_ROLE_ID
            )

            if residents_role:
                try:
                    if residents_role not in interaction.user.roles:
                        await interaction.user.add_roles(
                            residents_role,
                            reason="User completed intro"
                        )

                except discord.Forbidden:
                    print("[INTRO] Missing permission to add Residents role")

                except Exception as e:
                    print(f"[INTRO] Failed to add Residents role: {e}")

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
                        failed["game"]
                        for failed in failed_games
                    )
                    if failed_games
                    else "Tidak ada"
                ),
            }
        )
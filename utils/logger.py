import discord

from datetime import datetime
from utils.json_manager import (
    GUILD_SETTINGS_PATH,
    load_json,
)

# ======================
# SEND LOG
# ======================
async def send_log(
    guild: discord.Guild,
    log_type: str,
    action: str,
    user: discord.Member | discord.User,
    emoji: str,
    details: dict = None
):

    try:

        data = await load_json(GUILD_SETTINGS_PATH)
        guild_id = str(guild.id)

        if guild_id not in data:
            return

        log_channel_id = data[guild_id].get(
            "log_channel"
        )

        if not log_channel_id:
            return

        channel = guild.get_channel(
            log_channel_id
        )

        if not channel:
            return

        # ======================
        # COLOR
        # ======================
        color_map = {
            "SUCCESS": discord.Color.green(),
            "ERROR": discord.Color.red(),
            "INFORMATION": discord.Color.blurple(),
            "WARNING": discord.Color.orange()
        }
        
        action_name = {
            "Introduction": "Perkenalan",
            "Member Remove": "Keluar dari Server",
            "Member Join": "Masuk dan Bergabung di Server"
        }
        
        description_map = {
            "SUCCESS": f"User: <@{user.id}> berhasil saat melakukan **{action}**",
            "ERROR": f"User: <@{user.id}> gagal saat melakukan **{action}**",
            "WARNING": f"Peringatan saat user <@{user.id}> melakukan **{action}**",
            "INFORMATION": f"User <@{user.id}> telah **{action_name.get(action, action)}**"
        }

        embed = discord.Embed(
            title=f"{emoji}  • {log_type} LOGS",
            color=color_map.get(
                log_type,
                discord.Color.blurple()
            ),
            timestamp=datetime.now(),
            description=description_map.get(log_type)
        )

        # ======================
        # DETAILS
        # ======================
        if details:

            detail_text = ""

            for key, value in details.items():
                detail_text += (
                    f"*{key}:* {value}\n"
                )

            embed.add_field(
                name="Details",
                value=detail_text,
                inline=False
            )

        await channel.send(embed=embed)

    except Exception as e:
        print(f"ERROR LOGGER: {e}")
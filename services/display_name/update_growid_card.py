import logging

import discord

from database.core.intro_manager import (
    get_user_profile,
    save_intro_message,
)

from database.core.channel_manager import (
    get_channel,
)

from database.core.role_manager import (
    get_roles,
)

from services.card_generator import (
    get_avatar,
    generate_card,
)

from services.display_name.update_display_name import (
    update_display_name,
)


logger = logging.getLogger(__name__)

TARGET_GUILD_ID = 1030428036773990400
GAME_KEY = "growtopia"
BACKGROUND_NAME = "bg_gt.png"


async def update_growid_card(
    member: discord.Member,
) -> dict:
    if member.guild.id != TARGET_GUILD_ID:
        raise ValueError("Invalid target guild.")

    roles = await get_roles(member.guild.id) or {}

    pangkat_roles = roles.get(
        "by_group",
        {},
    ).get(
        "pangkat",
        {},
    )

    member_role_ids = {
        role.id
        for role in member.roles
    }

    if not member_role_ids.intersection(
        pangkat_roles.values()
    ):
        return {
            "success": False,
            "reason": "member_has_no_pangkat_role",
        }

    profile = await get_user_profile(
        guild_id=member.guild.id,
        user_id=member.id,
    )

    if not profile:
        return {
            "success": False,
            "reason": "profile_not_found",
        }

    game_data = profile.get(
        "games",
        {},
    ).get(
        GAME_KEY,
        {},
    )

    growid = game_data.get("value")

    if not growid or not growid.strip():
        return {
            "success": False,
            "reason": "growid_not_found",
        }

    channel_data = await get_channel(
        guild_id=member.guild.id,
        channel_key=GAME_KEY,
    )

    if not channel_data:
        return {
            "success": False,
            "reason": "channel_not_configured",
        }

    channel_id = channel_data.get("channel_id")

    channel = member.guild.get_channel(
        int(channel_id)
    )

    if channel is None:
        try:
            channel = await member.guild.fetch_channel(
                int(channel_id)
            )
        except discord.HTTPException:
            return {
                "success": False,
                "reason": "channel_not_found",
            }

    if not hasattr(channel, "send"):
        return {
            "success": False,
            "reason": "invalid_channel",
        }

    avatar = await get_avatar(
        member.display_avatar.url
    )

    card = await generate_card(
        avatar=avatar,
        user=member,
        game_text=growid.strip(),
        background_name=BACKGROUND_NAME,
        display_name=profile.get("nickname"),
        joined_at=profile.get("joined_at"),
    )

    card.seek(0)

    old_message_id = game_data.get(
        "message_id"
    )

    old_channel_id = game_data.get(
        "channel_id"
    )

    new_message = await channel.send(
        file=discord.File(
            fp=card,
            filename=f"growid_{member.id}.png",
        )
    )

    try:
        await save_intro_message(
            guild_id=member.guild.id,
            user_id=member.id,
            game_key=GAME_KEY,
            message_id=new_message.id,
            channel_id=channel.id,
        )

    except Exception:
        try:
            await new_message.delete()
        except discord.HTTPException:
            pass

        raise

    if old_message_id and old_channel_id:
        try:
            old_channel_id = int(old_channel_id)
            old_message_id = int(old_message_id)

            old_channel = member.guild.get_channel(
                old_channel_id
            )

            if old_channel is None:
                old_channel = await member.guild.fetch_channel(
                    old_channel_id
                )

            old_message = await old_channel.fetch_message(
                old_message_id
            )

            await old_message.delete()

        except discord.NotFound:
            pass

        except discord.Forbidden:
            logger.warning(
                "Cannot delete old GrowID card for user %s.",
                member.id,
            )

        except discord.HTTPException:
            logger.exception(
                "Failed to delete old GrowID card for user %s.",
                member.id,
            )

    display_name_updated = await update_display_name(
        member
    )

    return {
        "success": True,
        "message_id": new_message.id,
        "display_name_updated": display_name_updated,
    }
import asyncio
import discord

from database.delete_queue_manager import delete_queue_item

from services.clear_dm.protected import (
    get_protected_messages,
    is_protected
)

from services.clear_dm.target import (
    get_target_guild,
    get_target_members
)

# ==================================================
# GET DM CHANNEL
# ==================================================
async def get_dm_channel(
    member: discord.Member
):

    dm = member.dm_channel

    if dm is None:
        dm = await member.create_dm()

    return dm


# ==================================================
# DELETE MESSAGE
# ==================================================
async def delete_message(
    message: discord.Message
):

    await message.delete()

    try:
        await delete_queue_item(
            message.id
        )

    except Exception as e:
        print(
            f"[QUEUE DELETE ERROR] {e}"
        )

    await asyncio.sleep(0.5)
    
# ==================================================
# CLEAN MEMBER DM
# ==================================================
async def clean_member(
    bot,
    guild: discord.Guild,
    member: discord.Member
):

    deleted = 0
    failed = 0
    skipped = 0

    try:

        dm = await get_dm_channel(
            member
        )

        protected_messages = await get_protected_messages(member.id)

        async for message in dm.history(limit=None):

            # ======================
            # BOT MESSAGE ONLY
            # ======================
            if message.author.id != bot.user.id:
                continue

            # ======================
            # PROTECTED MESSAGE
            # ======================
            if is_protected(
                message.id,
                protected_messages
            ):

                skipped += 1

                print(
                    "[SKIP PROTECTED] "
                    f"user={member} "
                    f"msg_id={message.id}"
                )

                continue

            # ======================
            # DELETE
            # ======================
            try:

                print(
                    "[DELETE] "
                    f"user={member} "
                    f"msg_id={message.id}"
                )

                await delete_message(
                    message
                )

                deleted += 1

            except discord.NotFound:
                continue

            except discord.Forbidden:

                failed += 1

                print(
                    f"[FORBIDDEN] {member}"
                )

                break

            except Exception as e:

                failed += 1

                print(
                    f"[DELETE ERROR] {e}"
                )

    except Exception as e:

        failed += 1

        print(
            f"[FAILED USER] {member} | {e}"
        )

    return {
        "deleted": deleted,
        "failed": failed,
        "skipped": skipped
    }
    
# ==================================================
# CLEAR DM
# ==================================================
async def clear_dm(
    bot,
    interaction: discord.Interaction,
    guild_id: str | None,
    user: discord.Member | None
):

    guild = await get_target_guild(
        bot,
        interaction,
        guild_id
    )

    targets = await get_target_members(
        guild,
        user
    )

    result = {
        "guild": guild,
        "targets": len(targets),
        "deleted": 0,
        "failed": 0,
        "skipped": 0
    }

    for member in targets:

        member_result = await clean_member(
            bot,
            guild,
            member
        )

        result["deleted"] += member_result["deleted"]
        result["failed"] += member_result["failed"]
        result["skipped"] += member_result["skipped"]

    return result
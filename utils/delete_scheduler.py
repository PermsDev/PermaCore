import time
import asyncio
import discord

from database.delete_queue_manager import (
    upsert_delete_queue,
    get_expired_delete_queue,
    delete_queue_item
)
from utils.parse_duration import parse_duration

# =========================
# REGISTER MESSAGE DELETE
# =========================
async def register_delete(
    channel_id: int,
    message_id: int,
    delete_after
):
    if isinstance(delete_after, str):
        delete_after = parse_duration(
            delete_after
        )
        
    expire_time = (
        time.time() + delete_after
    )

    await upsert_delete_queue(
        channel_id,
        message_id,
        expire_time
    )


# =========================
# DELETE CHECKER
# =========================
async def delete_checker(bot):

    await bot.wait_until_ready()

    while not bot.is_closed():

        now = time.time()

        
        expired_items = await get_expired_delete_queue(now)

        for item in expired_items:

            try:

                channel = await bot.fetch_channel(
                    item["channel_id"]
                )

                message = await channel.fetch_message(
                    item["message_id"]
                )

                await message.delete()

                await delete_queue_item(item["message_id"])

            except discord.NotFound:

                await delete_queue_item(item["message_id"])

            except Exception as e:
                print(e)

        await asyncio.sleep(60)
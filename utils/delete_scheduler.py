import time
import asyncio
import discord
from utils.json_manager import (
    DELETE_QUEUE_PATH,
    load_json,
    save_json
)

# =========================
# REGISTER MESSAGE DELETE
# =========================
async def register_delete(
    channel_id: int,
    message_id: int,
    delete_after: int
):

    queue_data = await load_json(DELETE_QUEUE_PATH)

    expire_time = (
        time.time() + delete_after
    )

    found = False

    for item in queue_data:

        if (
            item["channel_id"] == channel_id
            and
            item["message_id"] == message_id
        ):

            item["delete_at"] = expire_time
            found = True
            break

    if not found:

        queue_data.append({
            "channel_id": channel_id,
            "message_id": message_id,
            "delete_at": expire_time
        })

    await save_json(
        DELETE_QUEUE_PATH,
        queue_data
    )


# =========================
# DELETE CHECKER
# =========================
async def delete_checker(bot):

    await bot.wait_until_ready()

    while not bot.is_closed():

        queue_data = await load_json(DELETE_QUEUE_PATH)

        now = time.time()

        remaining = []

        for item in queue_data:

            if now >= item["delete_at"]:

                try:

                    channel = await bot.fetch_channel(
                        item["channel_id"]
                    )

                    message = await channel.fetch_message(
                        item["message_id"]
                    )

                    await message.delete()

                except discord.NotFound:
                    pass

                except Exception as e:
                    print(e)

            else:

                remaining.append(item)

        await save_json(
            DELETE_QUEUE_PATH,
            remaining
        )

        await asyncio.sleep(5)
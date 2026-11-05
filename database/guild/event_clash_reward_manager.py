from asyncmy.cursors import DictCursor

from database.database import get_guild_pool as get_pool
from database.core.emoji_manager import get_emoji


def format_clash_reward(amount):

    amount = int(amount or 0)

    bgl = amount // 10000
    dl = (amount % 10000) // 100
    wl = amount % 100

    rewards = []

    if bgl:
        rewards.append(
            f"{bgl} {get_emoji('bgl')} "
        )

    if dl:
        rewards.append(
            f"{dl} {get_emoji('dl')} "
        )

    if wl:
        rewards.append(
            f"{wl} {get_emoji('wl')} "
        )

    return " ".join(rewards) if rewards else f"0 {get_emoji('wl')} "


async def get_clash_rewards(reward_type):

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute(
                """
                SELECT
                    id,
                    reward_type,
                    `rank`,
                    reward,
                    updated_at
                FROM event_clash_reward
                WHERE reward_type = %s
                ORDER BY `rank` ASC
                """,
                (reward_type,)
            )

            return await cursor.fetchall()


async def get_clash_reward(reward_type, rank):

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute(
                """
                SELECT
                    id,
                    reward_type,
                    `rank`,
                    reward,
                    updated_at
                FROM event_clash_reward
                WHERE reward_type = %s
                AND `rank` = %s
                LIMIT 1
                """,
                (reward_type, rank)
            )

            return await cursor.fetchone()
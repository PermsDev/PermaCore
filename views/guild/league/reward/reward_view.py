import discord

from database.core.emoji_manager import get_emoji
from database.guild.event_clash_reward_manager import (
    get_clash_rewards,
    format_clash_reward
)
from database.guild.event_clash_point_manager import get_clash_point


class RewardTopScoreView(discord.ui.LayoutView):

    def __init__(
        self,
        total_rewards,
        monthly_rewards,
        monthly_points
    ):
        super().__init__(timeout=None)

        components = [
            discord.ui.TextDisplay(
                content=(
                    f"## {get_emoji('GoldGuildChest')} Reward Top Score"
                )
            ),
            discord.ui.Separator(),
            discord.ui.TextDisplay(
                content="### 🏆 Top Total Score"
            )
        ]

        for rank in range(1, 6):

            reward = next(
                (
                    item["reward"]
                    for item in total_rewards
                    if item["rank"] == rank
                ),
                None
            )

            if reward is None:
                reward = f"-# {get_emoji('BlueArrow')} Reward not yet determined."
            else:
                reward = f"{get_emoji('BlueArrow')} {format_clash_reward(reward)}"

            if rank == 1:
                reward += " + **Guild Co-Leader**"

            components.append(
                discord.ui.TextDisplay(
                    content=(
                        f"**Rank {rank}**\n"
                        f"{reward}"
                    )
                )
            )

        components.extend([
            discord.ui.Separator(),
            discord.ui.TextDisplay(
                content="### 📅 Top Monthly Score"
            )
        ])

        for rank in range(1, 6):

            reward = next(
                (
                    item["reward"]
                    for item in monthly_rewards
                    if item["rank"] == rank
                ),
                None
            )

            score = next(
                (
                    item["points"]
                    for item in monthly_points
                    if item["rank_position"] == rank
                ),
                0
            )
            reward = format_clash_reward(reward)

            score_text = f"{score} Points"

            if rank == 1:
                score_text += " + **Guild Elder**"

            components.append(
                discord.ui.TextDisplay(
                    content=(
                        f"**Rank {rank}** » {reward}\n"
                        f"{get_emoji('RedArrow')} {score_text}"
                    )
                )
            )

        container = discord.ui.Container(*components)
        self.add_item(container)

    @classmethod
    async def create(cls):

        total_rewards = await get_clash_rewards(
            "total_score"
        )

        monthly_rewards = await get_clash_rewards(
            "monthly_score"
        )

        monthly_points = []

        for rank in range(1, 6):
            score = await get_clash_point(rank)

            monthly_points.append({
                "rank_position": rank,
                "points": score or 0
            })

        return cls(
            total_rewards=total_rewards,
            monthly_rewards=monthly_rewards,
            monthly_points=monthly_points
        )
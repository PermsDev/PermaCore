
import discord

from datetime import date

from database.core.emoji_manager import get_emoji

from views.guild.league.buttons import MoreTotalScoreButton, MoreMonthlyScoreButton

def create_top_score_components(
    total_scores: list[dict],
    monthly_scores: list[dict]
) -> discord.ui.Container:

    medal_emojis = {
        1: get_emoji("medal_1"),
        2: get_emoji("medal_2"),
        3: get_emoji("medal_3"),
        4: get_emoji("medal_4"),
        5: get_emoji("medal_5")
    }

    rank_emojis = {
        1: get_emoji("rank_1"),
        2: get_emoji("rank_2"),
        3: get_emoji("rank_3"),
        4: get_emoji("rank_4"),
        5: get_emoji("rank_5")
    }

    rank_emoji = get_emoji("rank")

    components = [
        discord.ui.TextDisplay(
            content=(
                f"# {rank_emoji} Perma Clash\n"
                "Perma Clash adalah sistem kompetisi komunitas untuk "
                "mencatat hasil, poin, peringkat, dan perkembangan pemain "
                "dalam setiap series."
            )
        ),
        discord.ui.Separator(
            visible=True,
            spacing=discord.SeparatorSpacing.large
        )
    ]

    total_limit = 5 if monthly_scores else 10

    total_lines = []

    if total_scores:

        for index, data in enumerate(
            total_scores[:total_limit],
            start=1
        ):

            growid = data["growid"] or "Unknown"
            points = data["total_points"]

            icon = rank_emojis.get(
                index,
                f"**{index}.**"
            )

            total_lines.append(
                f"{icon} `{growid}` — **{points} Point**"
            )

    else:
        total_lines.append(
            "Belum ada data."
        )

    components.append(
        discord.ui.Section(
            discord.ui.TextDisplay(
                content=f"### 🏆 Top {total_limit} Total Score"
            ),
            accessory=MoreTotalScoreButton()
        )
    )

    components.append(
        discord.ui.TextDisplay(
            content="\n".join(total_lines)
        )
    )

    if monthly_scores:

        components.append(
            discord.ui.Separator(
                visible=True,
                spacing=discord.SeparatorSpacing.large
            )
        )

        monthly_lines = []

        for data in monthly_scores[:5]:

            rank = data["rank_position"]
            growid = data["growid"] or "Unknown"
            points = data["points"]

            icon = medal_emojis.get(
                rank,
                f"**{rank}.**"
            )

            monthly_lines.append(
                f"{icon} `{growid}` — **{points} Point**"
            )

        components.append(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content="### 📅 Top 5 Score Bulan Ini"
                ),
                accessory=MoreMonthlyScoreButton()
            )
        )

        components.append(
            discord.ui.TextDisplay(
                content="\n".join(monthly_lines)
            )
        )

    if total_scores:

        series_name = total_scores[0]["series_name"]
        start_date = total_scores[0]["start_date"]
        end_date = total_scores[0]["end_date"]

        if isinstance(start_date, str):
            start_date = date.fromisoformat(
                start_date
            )

        if isinstance(end_date, str):
            end_date = date.fromisoformat(
                end_date
            )

        components.extend(
            [
                discord.ui.Separator(
                    visible=True,
                    spacing=discord.SeparatorSpacing.large
                ),
                discord.ui.TextDisplay(
                    content=(
                        f"-# 🏆 {series_name} · "
                        f"{start_date.year} ~ {end_date.year}"
                    )
                )
            ]
        )

    return discord.ui.Container(
        *components,
        accent_colour=15844367 if total_scores else None,
        spoiler=False
    )

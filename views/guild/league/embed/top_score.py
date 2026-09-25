from datetime import date

from database.core.emoji_manager import get_emoji


def create_top_score_components(
    total_scores: list[dict],
    monthly_scores: list[dict]
) -> list[dict]:

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
        {
            "type": 10,
            "content": (
                "# 🏆 Perma League\n"
                "Perma League adalah sistem kompetisi komunitas untuk "
                "mencatat hasil, poin, peringkat, dan perkembangan pemain "
                "dalam setiap season."
            )
        },
        {
            "type": 14,
            "divider": True,
            "spacing": 2
        }
    ]

    total_lines = []

    if total_scores:
        for index, data in enumerate(total_scores[:5], start=1):
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

    components.append({
        "type": 9,
        "components": [
            {
                "type": 10,
                "content": f"## {rank_emoji} Top 5 Total Score"
            }
        ],
        "accessory": {
            "type": 2,
            "style": 2,
            "label": "More",
            "custom_id": "league_more_total_score"
        }
    })

    components.append({
        "type": 10,
        "content": "\n".join(total_lines)
    })

    components.append({
        "type": 14,
        "divider": True,
        "spacing": 2
    })

    monthly_lines = []

    if monthly_scores:
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
    else:
        monthly_lines.append(
            "Belum ada data bulan ini."
        )

    components.append({
        "type": 9,
        "components": [
            {
                "type": 10,
                "content": "## 📅 Top 5 Score Bulan Ini"
            }
        ],
        "accessory": {
            "type": 2,
            "style": 2,
            "label": "More",
            "custom_id": "league_more_monthly_score"
        }
    })

    components.append({
        "type": 10,
        "content": "\n".join(monthly_lines)
    })

    if total_scores:
        series = total_scores[0]

        series_name = series["series_name"]
        start_date = series["start_date"]
        end_date = series["end_date"]

        if isinstance(start_date, str):
            start_date = date.fromisoformat(start_date)

        if isinstance(end_date, str):
            end_date = date.fromisoformat(end_date)

        components.extend([
            {
                "type": 14,
                "divider": True,
                "spacing": 2
            },
            {
                "type": 10,
                "content": (
                    f"-# 🏆 {series_name} · "
                    f"{start_date.year} ~ {end_date.year}"
                )
            }
        ])

    return components
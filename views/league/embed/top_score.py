from datetime import date

from database.core.emoji_manager import get_emoji


def create_top_score_components(
    total_scores: list[dict],
    monthly_scores: list[dict]
) -> list[dict]:
    
    MEDAL_1_EMOJI = get_emoji("medal_1")
    MEDAL_2_EMOJI = get_emoji("medal_2")
    MEDAL_3_EMOJI = get_emoji("medal_3")
    MEDAL_4_EMOJI = get_emoji("medal_4")
    MEDAL_5_EMOJI = get_emoji("medal_5")
    
    RANK_EMOJI = get_emoji("rank")
    RANK_1_EMOJI = get_emoji("rank_1")
    RANK_2_EMOJI = get_emoji("rank_2")
    RANK_3_EMOJI = get_emoji("rank_3")
    RANK_4_EMOJI = get_emoji("rank_4")
    RANK_5_EMOJI = get_emoji("rank_5")

    components = []

    components.append({
        "type": 10,
        "content": (
            "# 🏆 Perma League\n"
            "Perma League adalah sistem kompetisi komunitas untuk mencatat hasil, poin, peringkat, dan perkembangan pemain dalam setiap season."
        )
    })

    components.append({
        "type": 14,
        "divider": True,
        "spacing": 2
    })

    total_lines = []

    if total_scores:
        for index, data in enumerate(total_scores, start=1):
            growid = data["growid"] or "Unknown"
            points = data["total_points"]

            if index == 1:
                icon = RANK_1_EMOJI
            elif index == 2:
                icon = RANK_2_EMOJI
            elif index == 3:
                icon = RANK_3_EMOJI
            elif index == 4:
                icon = RANK_4_EMOJI
            elif index == 5:
                icon = RANK_5_EMOJI
            else:
                icon = f"**{index}.**"

            total_lines.append(
                f"{icon} `{growid}` — **{points} Point**"
            )
    else:
        total_lines.append(
            "Belum ada data."
        )

    components.append({
        "type": 10,
        "content": (
            f"## {RANK_EMOJI} Top 5 Total Score\n\n"
            + "\n".join(total_lines)
        )
    })

    components.append({
        "type": 14,
        "divider": True,
        "spacing": 2
    })

    monthly_lines = []

    if monthly_scores:
        for data in monthly_scores:
            rank = data["rank_position"]
            growid = data["growid"] or "Unknown"
            points = data["points"]

            if rank == 1:
                icon = MEDAL_1_EMOJI
            elif rank == 2:
                icon = MEDAL_2_EMOJI
            elif rank == 3:
                icon = MEDAL_3_EMOJI
            elif rank == 4:
                icon = MEDAL_4_EMOJI
            elif rank == 5:
                icon = MEDAL_5_EMOJI
            else:
                icon = f"**{rank}.**"

            monthly_lines.append(
                f"{icon} `{growid}` — **{points} Point**"
            )
    else:
        monthly_lines.append(
            "Belum ada data bulan ini."
        )

    components.append({
        "type": 10,
        "content": (
            "### 📅 Top 5 Score Bulan Ini\n\n"
            + "\n".join(monthly_lines)
        )
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

        start_year = start_date.year
        end_year = end_date.year
        
        components.append({
            "type": 14,
            "divider": True,
            "spacing": 2
        })

        components.append({
            "type": 10,
            "content": (
                f"-# 🏆  {series_name} · {start_year} ~ {end_year}"
            )
        })

    return components
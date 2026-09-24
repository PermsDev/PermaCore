from database.core.emoji_manager import get_emoji


def create_top_score_components(
    total_scores: list[dict],
    monthly_scores: list[dict]
) -> list[dict]:
    
    MEDAL_1 = get_emoji("medal_1")
    MEDAL_2 = get_emoji("medal_2")
    MEDAL_3 = get_emoji("medal_3")
    MEDAL_4 = get_emoji("medal_4")
    MEDAL_5 = get_emoji("medal_5")

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
                icon = MEDAL_1
            elif index == 2:
                icon = MEDAL_2
            elif index == 3:
                icon = MEDAL_3
            elif index == 4:
                icon = MEDAL_4
            elif index == 5:
                icon = MEDAL_5
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
            "### 🏆 Top 5 Total Score\n\n"
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
                icon = MEDAL_1
            elif rank == 2:
                icon = MEDAL_2
            elif rank == 3:
                icon = MEDAL_3
            elif rank == 4:
                icon = MEDAL_4
            elif rank == 5:
                icon = MEDAL_5
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
        components.append({
            "type": 14,
            "divider": True,
            "spacing": 2
        })

        components.append({
            "type": 10,
            "content": (
                f"-# 🏆 {total_scores[0]['series_name']}"
            )
        })

    return components
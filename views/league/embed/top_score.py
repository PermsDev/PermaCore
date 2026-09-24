import discord


def create_top_score_embed(
    total_scores: list[dict],
    monthly_scores: list[dict]
) -> discord.Embed:

    embed = discord.Embed(
        title="🏆 Event Clash Score",
        description=(
            "Ranking perolehan poin Event Clash."
        ),
        color=discord.Color.gold()
    )

    # =====================================================
    # TOP 5 TOTAL SCORE
    # =====================================================

    total_lines = []

    if total_scores:

        for index, data in enumerate(total_scores, start=1):

            growid = data["growid"] or "Unknown"
            points = data["total_points"]

            total_lines.append(
                f"**{index}.** `{growid}` — **{points} Point**"
            )

    else:

        total_lines.append(
            "Belum ada data."
        )

    embed.add_field(
        name="🏆 Top 5 Total Score",
        value="\n".join(total_lines),
        inline=False
    )

    # =====================================================
    # TOP 5 BULAN INI
    # =====================================================

    monthly_lines = []

    if monthly_scores:

        for data in monthly_scores:

            rank = data["rank_position"]
            growid = data["growid"] or "Unknown"
            points = data["points"]

            monthly_lines.append(
                f"**{rank}.** `{growid}` — **{points} Point**"
            )

    else:

        monthly_lines.append(
            "Belum ada data bulan ini."
        )

    embed.add_field(
        name="📅 Top 5 Score Bulan Ini",
        value="\n".join(monthly_lines),
        inline=False
    )

    # =====================================================
    # FOOTER
    # =====================================================

    if total_scores:

        embed.set_footer(
            text=total_scores[0]["series_name"]
        )

    return embed
from database.guild.event_clash_score_manager import (
    get_top_total_score,
    get_top_monthly_score
)

from views.league.embed.top_score import (
    create_top_score_components
)


async def create_top_score_panel() -> list[dict]:

    total_scores = await get_top_total_score()
    monthly_scores = await get_top_monthly_score()

    return create_top_score_components(
        total_scores,
        monthly_scores
    )
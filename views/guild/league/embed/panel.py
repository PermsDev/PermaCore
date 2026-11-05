
import discord

from datetime import date

from database.guild.event_clash_series_manager import get_all_series
from database.guild.event_clash_score_manager import (
    get_top_total_score,
    get_top_monthly_score
)

from views.guild.league.embed.top_score import create_top_score_components


async def create_top_score_panel(
    series_id: int | None = None
) -> discord.ui.LayoutView:

    series_list = await get_all_series()

    view = discord.ui.LayoutView(
        timeout=None
    )

    if not series_list:

        view.add_item(
            create_top_score_components(
                [],
                []
            )
        )

        return view

    if series_id is None:

        active_series = next(
            (
                series
                for series in series_list
                if series["status"] == "active"
            ),
            None
        )

        if active_series:
            series_id = active_series["series_id"]
        else:
            series_id = series_list[0]["series_id"]

    selected_series = next(
        (
            series
            for series in series_list
            if series["series_id"] == series_id
        ),
        None
    )

    if selected_series is None:

        view.add_item(
            create_top_score_components(
                [],
                []
            )
        )

        return view

    total_scores = await get_top_total_score(
        series_id
    )

    monthly_scores = []

    if selected_series["status"] == "active":

        monthly_scores = await get_top_monthly_score(
            series_id
        )

    view.add_item(
        create_top_score_components(
            total_scores,
            monthly_scores
        )
    )

    series_options = []

    for series in series_list[:25]:

        start_date = series["start_date"]
        end_date = series["end_date"]

        if isinstance(start_date, str):
            start_date = date.fromisoformat(
                start_date
            )

        if isinstance(end_date, str):
            end_date = date.fromisoformat(
                end_date
            )

        series_options.append(
            discord.SelectOption(
                label=series["series_name"][:100],
                value=str(series["series_id"]),
                description=(
                    f"{start_date.year} - {end_date.year}"
                )[:100]
            )
        )

    if series_options:

        select = discord.ui.Select(
            custom_id="league_select_series",
            placeholder="Pilih Series",
            min_values=1,
            max_values=1,
            options=series_options
        )

        view.add_item(
            discord.ui.ActionRow(select)
        )

    return view

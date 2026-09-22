from database.core.intro_manager import get_copyview_intros

from views.intro.copyValue.copy_view import CopyView


async def register_persistent_views(bot):

    for guild in bot.guilds:

        intros = await get_copyview_intros(
            guild.id
        )

        for intro in intros:

            bot.add_view(
                CopyView(
                    intro["game_key"],
                    str(intro["user_id"])
                )
            )
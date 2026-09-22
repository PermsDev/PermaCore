from database.main.user.display_name_manager import (
    get_or_create_display_source
)

from database.main.user.member_manager import (
    get_nickname
)

from database.core.intro_manager import (
    get_user_intro
)


async def get_display_name(
    guild_id: int,
    user_id: int
) -> str | None:

    # ======================
    # GET DISPLAY SOURCE
    # ======================

    source = await get_or_create_display_source(
        guild_id,
        user_id
    )

    # ======================
    # NICKNAME
    # ======================

    if source == "nickname":

        nickname = await get_nickname(
            user_id
        )

        return nickname.strip() if nickname else None

    # ======================
    # GET INTRO DATA
    # ======================

    if source in ("growid", "roblox"):

        intros = await get_user_intro(
            user_id
        )

        intro_map = {
            intro["game_key"]: intro["value"]
            for intro in intros
        }

        # ======================
        # GROWID
        # ======================

        if source == "growid":

            growid = intro_map.get(
                "growtopia"
            )

            return growid.strip() if growid else None

        # ======================
        # ROBLOX
        # ======================

        if source == "roblox":

            roblox = intro_map.get(
                "roblox"
            )

            return roblox.strip() if roblox else None

    return None
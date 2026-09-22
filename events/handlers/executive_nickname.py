import discord

from database.core.role_manager import get_roles
from database.main.user.display_name_manager import (
    set_display_source
)

from services.display_name.update_display_name import (
    update_display_name
)


async def handle_executive_nickname(
    before: discord.Member,
    after: discord.Member
):
    """
    Menangani perubahan role executive.

    Jika user mendapatkan:
        - executive_guild
        - executive_sinyalid

    maka display_source user diubah menjadi "growid".

    FORCE GROWID hanya dilakukan saat role didapatkan,
    bukan saat role dilepaskan.

    User tetap dapat mengubah display_source
    kembali melalui DisplayNameSelect.

    Setiap perubahan role executive tetap akan
    memicu update nickname Discord.
    """

    roles = await get_roles(
        after.guild.id
    )

    executive_roles = roles.get(
        "by_group",
        {}
    ).get(
        "executive",
        {}
    )

    if not executive_roles:
        return

    # ======================
    # ROLE CHANGES
    # ======================

    before_role_ids = {
        role.id
        for role in before.roles
    }

    after_role_ids = {
        role.id
        for role in after.roles
    }

    added_roles = (
        after_role_ids
        - before_role_ids
    )

    removed_roles = (
        before_role_ids
        - after_role_ids
    )

    changed_roles = (
        added_roles
        | removed_roles
    )

    # ======================
    # CHECK EXECUTIVE
    # ======================

    changed_executive_ids = (
        changed_roles
        & set(executive_roles.values())
    )

    if not changed_executive_ids:
        return

    # ======================
    # GET ROLE KEY
    # ======================

    changed_executive_keys = {
        role_key
        for role_key, role_id in executive_roles.items()
        if role_id in changed_executive_ids
    }

    # ======================
    # FORCE GROWID
    # ======================

    forced_growid_roles = {
        "executive_guild",
        "executive_sinyalid"
    }

    # Hanya role yang BARU DIDAPATKAN
    added_executive_ids = (
        added_roles
        & set(executive_roles.values())
    )

    added_executive_keys = {
        role_key
        for role_key, role_id in executive_roles.items()
        if role_id in added_executive_ids
    }

    if added_executive_keys & forced_growid_roles:

        await set_display_source(
            guild_id=after.guild.id,
            user_id=after.id,
            display_source="growid"
        )

    # ======================
    # UPDATE DISCORD NICKNAME
    # ======================

    await update_display_name(
        after
    )
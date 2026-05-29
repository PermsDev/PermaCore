from events.member_role_update import (
    get_role_groups
)

from utils.json_manager import (
    DM_MESSAGES_PATH,
    load_json
)

# =========================
# VERIFIED SYSTEM
# =========================
async def handle_verified(member):

    print(
        f"[VERIFIED] Checking {member}"
    )

    role_groups = await get_role_groups(
        member.guild.id
    )

    # =========================
    # VERIFIED GROUP
    # =========================
    verified_group = role_groups.get(
        "verified",
        {}
    )

    verified_role_id = verified_group.get(
        "verified_role"
    )

    verified_intro_id = verified_group.get(
        "verified_intro"
    )

    # =========================
    # RESIDENTS ROLE
    # =========================
    pangkat_group = role_groups.get("pangkat", {})
    residents_role_id = pangkat_group.get("residents")

    # =========================
    # INVALID DATA
    # =========================
    if not all([
        verified_role_id,
        verified_intro_id,
        residents_role_id
    ]):

        print(
            "[VERIFIED] Missing role configuration"
        )

        return

    member_role_ids = {
        role.id
        for role in member.roles
    }

    has_verified = (
        verified_role_id in member_role_ids
    )

    has_intro = (
        verified_intro_id in member_role_ids
    )

    print(
        f"[VERIFIED] "
        f"verified={has_verified} | "
        f"intro={has_intro}"
    )
    # =========================
    # UPDATE DM MESSAGE
    # =========================
    try:

        data = await load_json(
            DM_MESSAGES_PATH
        )

        guild_id = str(member.guild.id)
        user_id = str(member.id)

        user_data = (
            data
            .get(guild_id, {})
            .get(user_id, {})
        )

        welcome_dm_id = user_data.get(
            "welcome_dm_id"
        )

        if welcome_dm_id:

            dm_channel = await member.create_dm()

            dm_message = await dm_channel.fetch_message(
                welcome_dm_id
            )

            verified_emoji = (
                "<a:statusOnline:1478032492962250928>"
                if has_verified else
                "<a:statusOffline:1478032435164741777>"
            )

            intro_emoji = (
                "<a:statusOnline:1478032492962250928>"
                if has_intro else
                "<a:statusOffline:1478032435164741777>"
            )

            await dm_message.edit(
                content=(
                    "## Selamat datang di server! <a:hi_man:1478080922883719238>\n\n"

                    "Untuk Melanjutkan Progres Masuk Server, silahkan mendapatkan "
                    "2 role verified dengan cara dibawah ini:\n\n"

                    f"### {verified_emoji} "
                    "Role 1: Verified Roles (1)\n"

                    "- Kunjungi Channel "
                    "<#1030430669597327380>\n"

                    "- dan Click "
                    "[Here](https://discord.com/channels/"
                    "1030428036773990400/"
                    "customize-community)\n"

                    "- Klik reaction `Verified` "
                    "Sampai mendapatkan role "
                    "Verified 1\n\n"

                    f"### {intro_emoji} "
                    "Role 2: Verified Introduction (2)\n"

                    "- Kunjungi Channel "
                    "<#1501234394076020806>\n"

                    "- Atau click "
                    "[Here](https://discord.com/channels/"
                    "1030428036773990400/"
                    "1501234394076020806/"
                    "1506363733608239275)\n"

                    "- Isi formulir introduction "
                    "untuk mendapatkan role "
                    "Verified Introduction 2\n"
                )
            )

            print(
                f"[VERIFIED] DM updated for {member}"
            )

    except Exception as e:

        print(
            f"[VERIFIED] Failed update DM: {e}"
        )
        
    # =========================
    # VERIFIED COMPLETE
    # =========================
    if has_verified and has_intro:

        residents_role = member.guild.get_role(
            residents_role_id
        )

        if not residents_role:

            print(
                "[VERIFIED] Residents role not found"
            )

            return

        # =========================
        # ALREADY HAS ROLE
        # =========================
        if residents_role in member.roles:

            print(
                f"[VERIFIED] "
                f"{member} already has Residents"
            )

            return

        # =========================
        # ADD ROLE
        # =========================
        await member.add_roles(
            residents_role,
            reason=(
                "User completed verification"
            )
        )

        print(
            f"[VERIFIED] "
            f"Residents added to {member}"
        )

    else:

        print(
            f"[VERIFIED] "
            f"{member} has not completed verification"
        )
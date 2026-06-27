from database.database import get_pool

# =========================
# CACHE GLOBAL ROLE PER GUILD
# =========================

ROLE_CACHE = {}


async def load_roles(guild_id: int) -> dict:
    """
    Load semua role dari database berdasarkan guild_id
    lalu simpan ke cache.
    """

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    role_id,
                    role_key,
                    role_group
                FROM role_db
                WHERE guild_id = %s
            """, (guild_id,))

            rows = await cursor.fetchall()

    roles = {
        "by_key": {},
        "by_group": {}
    }

    for role_id, role_key, role_group in rows:

        role_id = int(role_id)

        roles["by_key"][role_key] = role_id

        roles["by_group"].setdefault(
            role_group,
            {}
        )[role_key] = role_id

    ROLE_CACHE[guild_id] = roles

    return roles


async def get_roles(guild_id: int) -> dict:
    """
    Ambil role dari cache.
    Jika belum ada maka load dari database.
    """

    if guild_id in ROLE_CACHE:
        return ROLE_CACHE[guild_id]

    return await load_roles(guild_id)


async def get_role_id(
    guild_id: int,
    role_key: str
):
    """
    Ambil role_id berdasarkan role_key.
    """

    roles = await get_roles(guild_id)

    return roles["by_key"].get(role_key)


async def get_roles_by_group(
    guild_id: int,
    group: str
) -> dict:
    """
    Ambil semua role dalam satu group.
    """

    roles = await get_roles(guild_id)

    return roles["by_group"].get(group, {})


async def get_no_rename_roles(
    guild_id: int
) -> set:
    """
    Mengambil semua role yang tidak boleh diubah.
    """

    roles = (await get_roles(guild_id))["by_key"]

    protected_roles = [
        "master_&_queen",
        "head_moderator",
        "admin_discord",
        "executive_guild",
        "executive_clan",
        "executive_sinyalid"
    ]

    return {
        roles[key]
        for key in protected_roles
        if key in roles
    }
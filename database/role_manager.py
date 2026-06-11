from database.database import get_connection


def get_roles(guild_id: int) -> dict:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT role_id, role_key
            FROM role_db
            WHERE guild_id = %s
            """,
            (guild_id,)
        )

        rows = cursor.fetchall()

        return {
            row["role_key"]: row["role_id"]
            for row in rows
        }

    finally:
        cursor.close()
        conn.close()


def get_role_id(
    guild_id: int,
    role_key: str
):
    roles = get_roles(guild_id)
    return roles.get(role_key)


def get_no_rename_roles(
    guild_id: int
):
    roles = get_roles(guild_id)

    protected_roles = {
        "MASTER",
        "HEAD_ADMIN",
        "EXECUTIVE_GUILD_ROLE_ID",
        "EXECUTIVE_CLAN_ROLE_ID",
        "EXECUTIVE_SINYALID_ROLE_ID"
    }

    result = set()

    for role_key in protected_roles:
        role_id = roles.get(role_key)

        if role_id:
            result.add(role_id)

    return result
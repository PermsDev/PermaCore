from database.database import get_connection

# =========================
# CACHE GLOBAL ROLE PER GUILD
# =========================
# Menyimpan data role yang sudah di-load dari database
# supaya tidak query ke MySQL setiap kali fungsi dipanggil

ROLE_CACHE = {}


def load_roles(guild_id: int) -> dict:
    """
    Load semua role dari database berdasarkan guild_id
    lalu menyimpannya ke cache (ROLE_CACHE)

    Struktur return:
    {
        "by_key": {
            role_key: role_id
        },
        "by_group": {
            role_group: {
                role_key: role_id
            }
        }
    }
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Ambil semua role untuk 1 guild
        cursor.execute(
            """
            SELECT role_id, role_key, role_group
            FROM role_db
            WHERE guild_id = %s
            """,
            (guild_id,)
        )

        rows = cursor.fetchall()

        # Struktur data hasil transformasi
        roles = {
            "by_key": {},     # akses cepat berdasarkan role_key
            "by_group": {}    # akses berdasarkan role_group
        }

        # Loop semua data dari database
        for row in rows:
            key = row["role_key"]
            group = row["role_group"]
            role_id = int(row["role_id"])

            # mapping role_key -> role_id
            roles["by_key"][key] = role_id

            # mapping role_group -> {role_key -> role_id}
            if group not in roles["by_group"]:
                roles["by_group"][group] = {}

            roles["by_group"][group][key] = role_id

        # simpan ke cache agar akses berikutnya lebih cepat
        ROLE_CACHE[guild_id] = roles

        return roles

    finally:
        # selalu tutup koneksi untuk mencegah memory leak
        cursor.close()
        conn.close()


def get_roles(guild_id: int) -> dict:
    """
    Mengambil semua role untuk guild tertentu.

    Prioritas:
    1. Ambil dari cache (ROLE_CACHE) jika sudah ada
    2. Jika belum ada, load dari database
    """

    # jika sudah ada di cache → pakai langsung
    if guild_id in ROLE_CACHE:
        return ROLE_CACHE[guild_id]

    # jika belum ada → ambil dari DB
    return load_roles(guild_id)


def get_role_id(guild_id: int, role_key: str):
    """
    Mengambil role_id berdasarkan role_key

    Contoh:
    get_role_id(guild_id, "admin_discord")
    -> 1133759724437905448
    """

    roles = get_roles(guild_id)
    return roles["by_key"].get(role_key)


def get_roles_by_group(guild_id: int, group: str) -> dict:
    """
    Mengambil semua role dalam satu group

    Contoh:
    group = "games"

    Return:
    {
        "mlbb": role_id,
        "minecraft": role_id,
        ...
    }
    """

    roles = get_roles(guild_id)
    return roles["by_group"].get(group, {})


def get_no_rename_roles(guild_id: int) -> set:
    """
    Mengambil semua role yang tidak boleh di-rename / diubah

    Ini biasanya dipakai untuk:
    - proteksi role penting
    - mencegah admin rename role sistem

    Return: set(role_id)
    """

    roles = get_roles(guild_id)["by_key"]

    # daftar role penting yang dilindungi
    protected_roles = [
        "master_&_queen",
        "head_moderator",
        "admin_discord",
        "executive_guild",
        "executive_clan",
        "executive_sinyalid"
    ]

    result = set()

    # ambil role_id dari role_key jika ada
    for key in protected_roles:
        if key in roles:
            result.add(roles[key])

    return result
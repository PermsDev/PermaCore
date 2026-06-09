import re

def validate_growid(value: str):
    """
    Growtopia:
    - 3-18 karakter
    - hanya huruf dan angka
    """
    if not value:
        return True, ""

    if not re.fullmatch(r"[A-Za-z0-9]{3,18}", value):
        return (
            False,
            "GrowID harus 3-18 karakter dan hanya boleh berisi huruf serta angka."
        )

    return True, ""


def validate_roblox(value: str):
    """
    Roblox:
    - 3-20 karakter
    - huruf, angka, underscore
    - underscore tidak boleh di awal/akhir
    - maksimal 1 underscore
    """
    if not value:
        return True, ""

    if len(value) < 3 or len(value) > 20:
        return (
            False,
            "Username Roblox harus terdiri dari 3-20 karakter."
        )

    if not re.fullmatch(r"[A-Za-z0-9_]+", value):
        return (
            False,
            "Username Roblox hanya boleh berisi huruf, angka, dan underscore (_)."
        )

    if value.startswith("_") or value.endswith("_"):
        return (
            False,
            "Underscore tidak boleh berada di awal atau akhir username."
        )

    if value.count("_") > 1:
        return (
            False,
            "Username Roblox hanya boleh memiliki satu underscore (_)."
        )

    return True, ""


def validate_pw(value: str):
    """
    Pixel Worlds:
    - 2-15 karakter
    - huruf, angka
    - simbol: _ - ^ { } [ ]
    """
    if not value:
        return True, ""

    if not re.fullmatch(r"[A-Za-z0-9_\-\^\{\}\[\]]{2,15}", value):
        return (
            False,
            "Username Pixel Worlds harus 2-15 karakter dan hanya boleh menggunakan huruf, angka, _, -, ^, { }, atau [ ]."
        )

    return True, ""

def validate_mlbb(value: str):
    """
    Mobile Legends:
    - hanya angka
    """
    if not value:
        return True, ""

    if not value.isdigit():
        return (
            False,
            "MLBB ID harus berupa angka."
        )

    return True, ""
# services/environment_service.py

import os


def get_app_env() -> str:
    return os.getenv(
        "APP_ENV",
        "development"
    ).lower()


def is_development() -> bool:
    return get_app_env() == "development"


def is_production() -> bool:
    return get_app_env() == "production"


def get_user_tester_id() -> int | None:
    user_id = os.getenv("USER_TESTER")

    if not user_id:
        return None

    try:
        return int(user_id)
    except ValueError:
        return None


def can_interact_with_user(user_id: int) -> bool:
    """
    Mengecek apakah user diizinkan menerima
    interaksi dari bot berdasarkan APP_ENV.
    """

    # Production: semua user diizinkan
    if is_production():
        return True

    # Development: hanya USER_TESTER
    if is_development():
        tester_id = get_user_tester_id()

        return user_id == tester_id

    # Environment tidak dikenal → blokir demi keamanan
    return False
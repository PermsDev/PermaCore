import re
import time


def discord_timestamp(
    duration: str,
    style: str = "R"
) -> str:

    match = re.fullmatch(
        r"(\d+)(m|h|d|w)",
        duration.lower().strip()
    )

    if not match:
        raise ValueError(
            "Duration harus menggunakan format "
            "seperti 1m, 1h, 1d, atau 1w."
        )

    value = int(match.group(1))
    unit = match.group(2)

    seconds = {
        "m": 60,
        "h": 60 * 60,
        "d": 60 * 60 * 24,
        "w": 60 * 60 * 24 * 7
    }

    timestamp = int(
        time.time() + (value * seconds[unit])
    )

    valid_styles = {
        "t",
        "T",
        "d",
        "D",
        "f",
        "F",
        "R"
    }

    if style not in valid_styles:
        raise ValueError(
            "Style timestamp tidak valid."
        )

    return f"<t:{timestamp}:{style}>"

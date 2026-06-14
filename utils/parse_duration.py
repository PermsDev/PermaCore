def parse_duration(duration: str) -> int:
    duration = duration.strip().lower()

    unit = duration[-1]
    value = int(duration[:-1])

    if unit == "m":
        return value * 60

    if unit == "h":
        return value * 60 * 60

    if unit == "d":
        return value * 24 * 60 * 60

    raise ValueError(
        f"Invalid duration format: {duration}"
    )
import os
from pathlib import Path
import json
import asyncio

# =========================
# LOCK
# =========================
lock = asyncio.Lock()

# =========================
# BASE DATA FOLDER
# =========================
DATA_DIR = Path("data")

# =========================
# JSON FILE PATHS
# =========================
GUILD_SETTINGS_PATH = (
    DATA_DIR / "guild_settings.json"
)

ROLE_GROUPS_PATH = (
    DATA_DIR / "role_groups.json"
)

GUILD_MESSAGES_PATH = (
    DATA_DIR
    / "messages"
    / "guild_messages.json"
)

EXECUTIVE_MESSAGES_PATH = (
    DATA_DIR
    / "messages"
    / "executive_messages.json"
)

DM_MESSAGES_PATH = (
    DATA_DIR
    / "messages"
    / "dm_messages.json"
)

DELETE_QUEUE_PATH = (
    DATA_DIR
    / "messages"
    / "delete_queue.json"
)

INTRO_DATA_PATH = (
    DATA_DIR 
    / "intro_data.json"
)

FEEDBACK_PATH = (
    DATA_DIR
    / "feedbacks.json"
)

# =========================
# LOAD JSON
# =========================
async def load_json(path: Path):

    # file tidak ada
    if not path.exists():
        return {}

    # buka file
    async with lock:
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

# =========================
# SAVE JSON
# =========================
async def save_json(
    path: Path,
    data
):

    async with lock:

        # pastikan folder ada
        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(path, "w", encoding="utf-8") as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

async def update_json(
    path : Path,
    callback
):
    async with lock:
        
        if not os.path.exists(path):
            data = {}
        else:
            
            with open(path , "r", encoding="utf-8") as f:
                data = json.load(f)
        callback(data)

        with open(path , "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

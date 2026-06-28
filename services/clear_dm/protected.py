from database.dm_message_manager import get_user_dm_messages


# ==================================================
# GET PROTECTED MESSAGE IDS
# ==================================================
async def get_protected_messages(
    user_id: int
) -> set[int]:

    return await get_user_dm_messages(user_id)


# ==================================================
# CHECK PROTECTED
# ==================================================
def is_protected(
    message_id: int,
    protected_messages: set[int]
) -> bool:

    return message_id in protected_messages
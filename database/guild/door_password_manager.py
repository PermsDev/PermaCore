import os

from cryptography.fernet import Fernet

from database.database import get_guild_pool as get_pool


DOOR_PASSWORD_KEY = os.getenv("DOOR_PASSWORD_KEY")

if not DOOR_PASSWORD_KEY:
    raise RuntimeError("DOOR_PASSWORD_KEY is not configured")


fernet = Fernet(
    DOOR_PASSWORD_KEY.encode()
)


def encrypt_password(
    password: str | None
) -> str | None:

    if password is None:
        return None

    return fernet.encrypt(
        password.encode()
    ).decode()


def decrypt_password(
    encrypted_password: str | None
) -> str | None:

    if encrypted_password is None:
        return None

    return fernet.decrypt(
        encrypted_password.encode()
    ).decode()


async def get_door_password(
    guild_id: int,
    pass_id: int
) -> dict | None:

    pool = get_pool()

    async with pool.acquire() as conn:

        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    pass_id,
                    guild_id,
                    world_name,
                    name_door,
                    pass_door,
                    is_shared,
                    created_at,
                    updated_at
                FROM guild_door_password
                WHERE guild_id = %s
                AND pass_id = %s
                LIMIT 1
                """,
                (
                    guild_id,
                    pass_id
                )
            )

            row = await cursor.fetchone()

            if row is None:
                return None

            return {
                "pass_id": row[0],
                "guild_id": row[1],
                "world_name": row[2],
                "name_door": row[3],
                "pass_door": decrypt_password(row[4]),
                "is_shared": bool(row[5]),
                "created_at": row[6],
                "updated_at": row[7]
            }


async def update_door_password(
    guild_id: int,
    pass_id: int,
    pass_door: str | None
) -> dict | None:

    pool = get_pool()

    async with pool.acquire() as conn:

        async with conn.cursor() as cursor:

            encrypted_password = encrypt_password(
                pass_door
            )

            await cursor.execute(
                """
                UPDATE guild_door_password
                SET
                    pass_door = %s,
                    is_shared = 0
                WHERE guild_id = %s
                AND pass_id = %s
                """,
                (
                    encrypted_password,
                    guild_id,
                    pass_id
                )
            )

            if cursor.rowcount == 0:
                await conn.rollback()
                return None

            await conn.commit()

    return await get_door_password(
        guild_id=guild_id,
        pass_id=pass_id
    )


async def update_door_shared(
    guild_id: int,
    pass_id: int
) -> dict | None:

    pool = get_pool()

    async with pool.acquire() as conn:

        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                UPDATE guild_door_password
                SET
                    is_shared = 1
                WHERE guild_id = %s
                AND pass_id = %s
                """,
                (
                    guild_id,
                    pass_id
                )
            )

            if cursor.rowcount == 0:
                await conn.rollback()
                return None

            await conn.commit()

    return await get_door_password(
        guild_id=guild_id,
        pass_id=pass_id
    )
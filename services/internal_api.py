import hmac
import logging
import os

import discord
from aiohttp import web

from services.display_name.update_growid_card import (
    update_growid_card,
)


logger = logging.getLogger(__name__)

TARGET_GUILD_ID = 1030428036773990400

_api_runner = None
_api_site = None


async def update_growid_card_endpoint(
    request: web.Request,
) -> web.Response:
    expected_token = request.app["api_token"]
    authorization = request.headers.get(
        "Authorization",
        "",
    )

    expected_authorization = f"Bearer {expected_token}"

    if not hmac.compare_digest(
        authorization,
        expected_authorization,
    ):
        return web.json_response(
            {
                "success": False,
                "error": "unauthorized",
            },
            status=401,
        )

    try:
        payload = await request.json()
    except (ValueError, TypeError):
        return web.json_response(
            {
                "success": False,
                "error": "invalid_json",
            },
            status=400,
        )

    if not isinstance(payload, dict):
        return web.json_response(
            {
                "success": False,
                "error": "invalid_payload",
            },
            status=400,
        )

    try:
        user_id = int(payload["user_id"])

        if user_id <= 0:
            raise ValueError

    except (KeyError, TypeError, ValueError):
        return web.json_response(
            {
                "success": False,
                "error": "invalid_user_id",
            },
            status=400,
        )

    bot = request.app["bot"]

    guild = bot.get_guild(TARGET_GUILD_ID)

    if guild is None:
        return web.json_response(
            {
                "success": False,
                "error": "target_guild_not_available",
            },
            status=503,
        )

    member = guild.get_member(user_id)

    if member is None:
        try:
            member = await guild.fetch_member(user_id)

        except discord.NotFound:
            return web.json_response(
                {
                    "success": False,
                    "error": "member_not_found",
                },
                status=404,
            )

        except discord.Forbidden:
            return web.json_response(
                {
                    "success": False,
                    "error": "member_fetch_forbidden",
                },
                status=403,
            )

        except discord.HTTPException:
            logger.exception(
                "Failed to fetch member %s.",
                user_id,
            )

            return web.json_response(
                {
                    "success": False,
                    "error": "member_fetch_failed",
                },
                status=502,
            )

    try:
        result = await update_growid_card(member)

        return web.json_response(result)

    except Exception:
        logger.exception(
            "Failed to update GrowID card for user %s.",
            user_id,
        )

        return web.json_response(
            {
                "success": False,
                "error": "growid_card_update_failed",
            },
            status=500,
        )


async def start_internal_api(bot):
    global _api_runner, _api_site

    if _api_runner is not None:
        return

    api_token = os.getenv(
        "INTERNAL_API_TOKEN",
        "",
    ).strip()

    if not api_token:
        raise RuntimeError(
            "INTERNAL_API_TOKEN is not configured."
        )

    host = os.getenv(
        "INTERNAL_API_HOST",
        "0.0.0.0",
    )

    port = int(
        os.getenv(
            "INTERNAL_API_PORT",
            "8765",
        )
    )

    app = web.Application()
    app["bot"] = bot
    app["api_token"] = api_token

    app.router.add_post(
        "/internal/update-growid-card",
        update_growid_card_endpoint,
    )

    _api_runner = web.AppRunner(app)
    await _api_runner.setup()

    try:
        _api_site = web.TCPSite(
            _api_runner,
            host,
            port,
        )

        await _api_site.start()

    except Exception:
        await _api_runner.cleanup()
        _api_runner = None
        _api_site = None
        raise

    logger.info(
        "Internal API started on %s:%s",
        host,
        port,
    )


async def stop_internal_api():
    global _api_runner, _api_site

    if _api_runner is None:
        return

    await _api_runner.cleanup()

    _api_runner = None
    _api_site = None

    logger.info("Internal API stopped.")
import asyncio
import logging
import aiohttp

log = logging.getLogger("Heartbeat")


class HeartbeatTask:

    def __init__(
        self,
        url: str,
        interval: int = 30
    ):
        self.url = url
        self.interval = interval
        self.session = None

    async def start(self):

        self.session = aiohttp.ClientSession()

        while True:

            try:

                async with self.session.get(self.url) as response:

                    if response.status == 200:
                        log.info("Heartbeat sent.")
                    else:
                        log.warning(
                            f"Heartbeat failed ({response.status})"
                        )

            except Exception as e:

                log.error(
                    f"Heartbeat Error : {e}"
                )

            await asyncio.sleep(self.interval)

    async def close(self):

        if self.session:
            await self.session.close()
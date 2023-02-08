import asyncio

from anti_useragent import UserAgent
from httpx import AsyncClient, Response
from loguru import logger

from config import HEADERS


def get_modified_headers() -> dict:
    headers = HEADERS.copy()
    headers["User-Agent"] = UserAgent().random

    return headers


class Shardeum():
    def __init__(self):
        self._client = AsyncClient(
            base_url="https://shardeum.org",
            headers=get_modified_headers(),
            follow_redirects=True
        )

    def __del__(self):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._client.aclose())
            else:
                loop.run_until_complete(self._client.aclose())
        except Exception:
            pass

    async def request(self, method: str, url: str, json: dict | None = None) -> Response:
        response = await self._client.request(method=method, url=url, json=json)

        logger.info(
            f"{method} {response.url} Response: '{response.status_code} "
            f"{response.reason_phrase}' {response.text}"
        )

        return response
    
    async def auth_session(self):
        return await self.request("GET", "/api/auth/session")

    async def subscribe_newsletter(self, email):
        return await self.request(
            "POST",
            "/api/newsletter",
            json={
                "email": email,
                "source":["newsletterHero"]
            }
        )


async def subscribe_shardeum(queue: asyncio.Queue):
    while not queue.empty():
        shardeum = Shardeum()

        await shardeum.auth_session()
        await shardeum.subscribe_newsletter(await queue.get())

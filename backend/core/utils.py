import httpx
from bs4 import BeautifulSoup as bs

from .const import SITE_HOST


def is_site_host(url: str):
    return bool(url.startswith(SITE_HOST))


async def get_soup(url: str) -> bs:
    async with httpx.AsyncClient() as client:
        return bs(
            (await client.get(url)).text,
            "lxml",
        )

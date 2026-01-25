from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import Optional

import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@dataclass
class HttpClient:
    timeout_s: int = 30
    user_agent: str = "kenyalaw-scraper/0.1 (research; contact=you@example.com)"
    concurrency: int = 20

    def __post_init__(self) -> None:
        self._sem = asyncio.Semaphore(self.concurrency)

    async def __aenter__(self) -> "HttpClient":
        timeout = aiohttp.ClientTimeout(total=self.timeout_s)
        self._session = aiohttp.ClientSession(
            timeout=timeout,
            headers={"User-Agent": self.user_agent},
        )
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._session.close()

    @retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
    )
    async def get_text(self, url: str) -> str:
        async with self._sem:
            async with self._session.get(url) as r:
                r.raise_for_status()
                return await r.text()

    @retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
    )
    async def download_bytes(self, url: str) -> bytes:
        async with self._sem:
            async with self._session.get(url) as r:
                r.raise_for_status()
                return await r.read()

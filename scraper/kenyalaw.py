import asyncio
import logging
from typing import List, Optional
from urllib.parse import urljoin

import aiohttp

from scraper.url_finder import find_case_links
from scraper.case_scraper import extract_case_from_html
from models.case import Case
from config.settings import SETTINGS

logger = logging.getLogger(__name__)


class KenyaLawScraper:
    def __init__(self, base_url: str = None, max_concurrency: int = 4, delay: float = 0.5):
        self.base_url = base_url or SETTINGS["BASE_URL"]
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._delay = float(delay)
        self._session: Optional[aiohttp.ClientSession] = None
        self.headers = {"User-Agent": SETTINGS["DEFAULT_USER_AGENT"]}

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, *args):
        if self._session:
            await self._session.close()

    async def _fetch(self, url: str, timeout: int = None) -> Optional[str]:
        timeout = timeout or int(SETTINGS.get("REQUEST_TIMEOUT", 20))
        attempt = 0
        max_attempts = 3
        while attempt < max_attempts:
            try:
                async with self._semaphore:
                    if self._delay:
                        await asyncio.sleep(self._delay)
                    assert self._session is not None
                    async with self._session.get(url, timeout=timeout) as resp:
                        resp.raise_for_status()
                        text = await resp.text()
                        return text
            except Exception as e:
                attempt += 1
                logger.debug("Fetch error for %s (attempt %d/%d): %s", url, attempt, max_attempts, e)
                await asyncio.sleep(0.5 * attempt)
        logger.warning("Failed to fetch %s after %d attempts", url, max_attempts)
        return None

    async def scrape_index(self, index_url: str = None, limit: int = 10) -> List[str]:
        index_url = index_url or urljoin(self.base_url, SETTINGS["INDEX_PATH"])
        html = await self._fetch(index_url)
        if not html:
            return []
        links = find_case_links(html, self.base_url, limit=limit)
        logger.info("Found %d links on index %s", len(links), index_url)
        return links

    async def scrape_case_page(self, case_url: str) -> Optional[Case]:
        html = await self._fetch(case_url)
        if not html:
            return None
        case = extract_case_from_html(html, case_url)
        if case:
            logger.info("Scraped case %s", case.case_id)
        return case

    async def scrape_many_cases(self, urls: List[str]) -> List[Optional[Case]]:
        tasks = [self.scrape_case_page(u) for u in urls]
        results = await asyncio.gather(*tasks)
        return results
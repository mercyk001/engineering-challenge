from typing import List
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from scraper.selectors import INDEX_SELECTORS


def find_case_links(html: str, base_url: str, limit: int = 20) -> List[str]:
    soup = BeautifulSoup(html, "lxml")
    links = []
    seen = set()
    for sel in INDEX_SELECTORS:
        for a in soup.select(sel):
            href = a.get("href")
            if not href:
                continue
            full = urljoin(base_url, href)
            if full not in seen:
                seen.add(full)
                links.append(full)
            if len(links) >= limit:
                return links[:limit]
    # fallback: any anchor
    if not links:
        for a in soup.find_all("a", href=True):
            full = urljoin(base_url, a["href"])
            if full not in seen:
                seen.add(full)
                links.append(full)
            if len(links) >= limit:
                break
    return links[:limit]
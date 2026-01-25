
import argparse
import asyncio
import logging
import os
from datetime import datetime

from config.settings import SETTINGS
from config.logging_config import configure_logging
from scraper.kenyalaw import KenyaLawScraper
from storage.file_handler import save_json

configure_logging()
logger = logging.getLogger("kenyalaw")

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)


async def run(limit: int = 10, index_url: str | None = None):
    async with KenyaLawScraper(base_url=SETTINGS["BASE_URL"],
                              max_concurrency=SETTINGS["MAX_CONCURRENCY"],
                              delay=SETTINGS["REQUEST_DELAY"]) as scraper:
        urls = await scraper.scrape_index(index_url=index_url, limit=limit)
        if not urls:
            logger.warning("No links discovered from index %s", index_url or SETTINGS["INDEX_PATH"])
            return []

        logger.info("Discovered %d candidate links", len(urls))
        results = await scraper.scrape_many_cases(urls)
        cases = [c.to_dict() for c in results if c]

        if cases:
            fname = os.path.join(OUTPUT_DIR, f"cases_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json")
            save_json(fname, cases)
            logger.info("Saved %d cases to %s", len(cases), fname)
        else:
            logger.info("No cases scraped")
        return cases


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Kenya Law scraper (Level 1)")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of cases to fetch")
    parser.add_argument("--index", type=str, default=None, help="Index URL to discover cases from (optional)")
    args = parser.parse_args()

    asyncio.run(run(limit=args.limit, index_url=args.index))
import asyncio
from typing import List

class ConcurrentScraper:
    async def scrape_multiple_cases(self, urls: List[str]):
        
        tasks = []
        for url in urls:
            task = asyncio.create_task(self.scrape_case_page(url))
            tasks.append(task)
        
        cases = await asyncio.gather(*tasks, return_exceptions=True)
        return [c for c in cases if c is not None]
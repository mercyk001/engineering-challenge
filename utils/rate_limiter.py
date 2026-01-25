import asyncio
from contextlib import asynccontextmanager


class AsyncRateLimiter:
    def __init__(self, max_concurrency: int = 4, delay: float = 0.5):
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.delay = delay

    @asynccontextmanager
    async def acquire(self):
        async with self.semaphore:
            if self.delay:
                await asyncio.sleep(self.delay)
            yield
import asyncio
from typing import Iterable, Callable, Any, List


async def gather_with_concurrency(n: int, *tasks: Iterable[Callable[..., Any]]):
   
    semaphore = asyncio.Semaphore(n)

    async def sem_task(coro):
        async with semaphore:
            return await coro

    return await asyncio.gather(*[sem_task(t) for t in tasks])
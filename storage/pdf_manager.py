import os
from urllib.parse import urlparse
import aiohttp
import asyncio

PDF_DIR = "pdfs"
os.makedirs(PDF_DIR, exist_ok=True)


async def download_pdf(session: aiohttp.ClientSession, url: str, dest_dir: str = PDF_DIR, timeout: int = 60) -> str | None:
    if not url:
        return None
    filename = os.path.basename(urlparse(url).path) or "document.pdf"
    dest = os.path.join(dest_dir, filename)
    try:
        async with session.get(url, timeout=timeout) as resp:
            resp.raise_for_status()
            data = await resp.read()
            with open(dest, "wb") as f:
                f.write(data)
        return dest
    except Exception:
        return None
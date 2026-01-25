import re
from typing import List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from models.legislation import Legislation


def extract_legislation_from_html(html: str, url: str) -> Optional[Legislation]:
    soup = BeautifulSoup(html, "lxml")
    title = soup.select_one("h1")
    title_text = title.get_text(strip=True) if title else ""

    # chapter/number heuristics
    chapter = None
    ch = soup.find(lambda t: t.name in ("p", "div", "span", "li") and "Chapter" in t.get_text())
    if ch:
        chapter = ch.get_text(" ", strip=True)

    # year heuristics
    m = re.search(r"\b(19|20)\d{2}\b", soup.get_text(" ", strip=True))
    year = int(m.group(0)) if m else None

    # download pdf
    a_pdf = soup.find("a", href=re.compile(r"\.pdf$", re.IGNORECASE))
    download_url = urljoin(url, a_pdf["href"]) if a_pdf else None

    # last revision
    last_revision = None
    rev = soup.find(lambda t: "Last revised" in t.get_text() if t else False)
    if rev:
        last_revision = rev.get_text(" ", strip=True)

    # category heuristics (very basic keyword mapping)
    txt = soup.get_text(" ", strip=True).lower()
    if "criminal" in txt:
        category = "Criminal"
    elif "constitution" in txt:
        category = "Constitutional"
    elif "tax" in txt:
        category = "Tax"
    else:
        category = "General"

    leg = Legislation(
        act_id=(download_url or url),
        title=title_text or url,
        chapter=chapter,
        year=year,
        download_url=download_url,
        last_revision_date=last_revision,
        category=category,
        raw_text=soup.get_text("\n", strip=True),
    )
    return leg
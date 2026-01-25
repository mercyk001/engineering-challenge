from __future__ import annotations
import re
from bs4 import BeautifulSoup
from typing import Dict, Iterable, List, Optional, Tuple

AKN_ID_RE = re.compile(r"/akn/ke/[^?]+")  # keep it simple for doc_id derivation

def canonical_doc_id(url: str) -> str:
    """
    Derive a stable ID from the AKN path, e.g.
    https://new.kenyalaw.org/akn/ke/judgment/kesc/2025/75/eng@2025-12-11
    """
    m = AKN_ID_RE.search(url)
    return (m.group(0).strip("/").replace("/", "_") if m else re.sub(r"\W+", "_", url))

def parse_list_page_for_case_links(html: str, base_url: str = "https://new.kenyalaw.org") -> List[str]:
    """
    Extract detail-page links from a court list page (e.g. /judgments/KESC/).
    The list contains anchors pointing to /akn/... detail pages. (See example list+click flow.) :contentReference[oaicite:7]{index=7}
    """
    soup = BeautifulSoup(html, "lxml")
    links = []
    for a in soup.select("a[href]"):
        href = a["href"]
        if href.startswith("/akn/ke/") and "/judgment/" in href:
            links.append(base_url + href)
    return sorted(set(links))

def parse_detail_page(html: str, url: str, base_url: str = "https://new.kenyalaw.org") -> Tuple[str, Dict[str, str], Optional[str], Optional[str]]:
    """
    Returns:
      title, metadata dict, pdf_url, docx_url
    """
    soup = BeautifulSoup(html, "lxml")

    h1 = soup.select_one("h1")
    title = h1.get_text(" ", strip=True) if h1 else url

    # Download links often appear near "Download DOCX" + "Download PDF" :contentReference[oaicite:8]{index=8}
    pdf_url = None
    docx_url = None
    for a in soup.select("a[href]"):
        text = a.get_text(" ", strip=True).lower()
        href = a["href"]
        if "download pdf" in text:
            pdf_url = href if href.startswith("http") else base_url + href
        if "download docx" in text or ("original source file" in soup.get_text(" ").lower() and href.endswith(".docx")):
            docx_url = href if href.startswith("http") else base_url + href

    # Simple key/value scrape from the “Document detail” section
    metadata: Dict[str, str] = {}
    # This is intentionally flexible: site HTML can change.
    # Strategy: look for labels then the following text node.
    labels = ["Court", "Court station", "Case number", "Attorneys", "Judges", "Judgment date", "Type", "Language"]
    page_text = soup.get_text("\n", strip=True)
    for lab in labels:
        if lab in page_text:
            # fallback heuristic; you can replace with a more precise DOM traversal
            pass

    return title, metadata, pdf_url, docx_url

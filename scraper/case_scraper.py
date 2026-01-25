import re
from typing import Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from models.case import Case
from scraper.selectors import TITLE_SELECTORS, SUMMARY_SELECTORS, PDF_SELECTOR


def _slug_from_url(url: str) -> str:
    p = urlparse(url).path.strip("/").replace("/", "_")
    return p or "case_unknown"


def extract_case_from_html(html: str, url: str) -> Optional[Case]:
    soup = BeautifulSoup(html, "lxml")
    # Title
    title = ""
    for sel in TITLE_SELECTORS:
        el = soup.select_one(sel)
        if el:
            if el.name == "meta":
                title = el.get("content", "").strip()
            else:
                title = el.get_text(strip=True)
            if title:
                break

    # Raw text fallback
    body_text = soup.get_text("\n", strip=True)

    # Citation
    citation = ""
    m = re.search(r"\[\s*(20\d{2})\s*\][^\n]{0,60}eKLR[^\n]*", body_text, re.IGNORECASE)
    if m:
        citation = m.group(0)
    else:
        # try label
        label = soup.find(lambda t: t.name in ("p", "div", "span", "li") and "Citation" in t.get_text())
        if label:
            citation = label.get_text(" ", strip=True)

    # Court
    court = ""
    cnode = soup.find(lambda t: t.name in ("p", "div", "span", "li") and "Court" in t.get_text())
    if cnode:
        court = re.sub(r"^.*Court[:\s]*", "", cnode.get_text(" ", strip=True))

    # Date
    judgement_date = ""
    time_tag = soup.find("time")
    if time_tag and time_tag.get("datetime"):
        judgement_date = time_tag["datetime"]
    elif time_tag:
        judgement_date = time_tag.get_text(strip=True)
    else:
        dnode = soup.find(lambda t: t.name in ("p", "div", "span", "li") and "Date" in t.get_text())
        if dnode:
            judgement_date = re.sub(r"^.*Date[:\s]*", "", dnode.get_text(" ", strip=True))
        else:
            dm = re.search(r"\b(?:\d{1,2}\s+\w+\s+20\d{2}|\w+\s+\d{1,2},\s*20\d{2}|\d{4}-\d{2}-\d{2})\b", body_text)
            if dm:
                judgement_date = dm.group(0)

    # Judges
    judges = []
    for p in ("Coram", "Before", "Delivered by", "Judge", "Judges"):
        node = soup.find(lambda t: t.name in ("p", "div", "span", "li") and p in t.get_text())
        if node:
            txt = re.sub(rf"^.*{p}[:\s]*", "", node.get_text(" ", strip=True))
            parts = re.split(r",|;| and | & ", txt)
            judges.extend([pp.strip() for pp in parts if pp.strip()])
    judges = list(dict.fromkeys(judges))

    # Parties basic heuristic
    parties = {}
    between_node = soup.find(lambda t: t.name in ("p", "div", "section") and t.get_text().strip().startswith("Between"))
    if between_node:
        txt = between_node.get_text(" ", strip=True)
        core = re.sub(r"^Between[:\s]*", "", txt, flags=re.IGNORECASE)
        parts = re.split(r"\s+v(?:s)?\.?\s+|\s+versus\s+|\s+vs\.?\s+", core, flags=re.IGNORECASE)
        if len(parts) >= 2:
            parties["plaintiff"] = [parts[0].strip()]
            parties["defendant"] = [parts[1].strip()]

    if not parties:
        for label in ("Plaintiff", "Applicant", "Respondent", "Defendant"):
            node = soup.find(lambda t: t.name in ("p", "div", "li") and label in t.get_text())
            if node:
                m = re.search(rf"{label}[:\s]*(.+)", node.get_text(" ", strip=True))
                if m:
                    parties.setdefault(label.lower(), []).append(m.group(1).strip())

    # Summary
    summary = ""
    for sel in SUMMARY_SELECTORS:
        el = soup.select_one(sel)
        if el and el.get_text(strip=True):
            summary = el.get_text(" ", strip=True)
            break

    if not summary:
        p = soup.select_one("article p, main p, .document p, .content p")
        if p:
            summary = p.get_text(" ", strip=True)

    # Full text
    candidates = ["article", "main", ".document", ".judgement-body", ".case-content", "#content"]
    full_text = ""
    for sel in candidates:
        node = soup.select_one(sel)
        if node:
            full_text = node.get_text("\n", strip=True)
            if len(full_text) > 200:
                break
    if not full_text:
        full_text = body_text

    # PDF
    a_pdf = soup.select_one(PDF_SELECTOR)
    pdf_url = urljoin(url, a_pdf["href"]) if a_pdf else None

    # id
    case_id = ""
    if citation:
        case_id = re.sub(r"[^\w\-\.]+", "_", citation).strip("_").lower()
    if not case_id:
        case_id = _slug_from_url(url)

    case = Case(
        case_id=case_id,
        title=title or "",
        citation=citation or "",
        court=court or "",
        judge=judges or [],
        judgement_date=judgement_date or "",
        parties=parties or {},
        summary=summary or "",
        url=url,
        pdf_url=pdf_url,
        raw_text=full_text or "",
    )

    return case
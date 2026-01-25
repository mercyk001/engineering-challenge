from __future__ import annotations
import re
from typing import List

VS_SPLIT_RE = re.compile(r"\s+v(?:s\.)?\s+", re.IGNORECASE)

def normalize_party(p: str) -> str:
    p = re.sub(r"\s+", " ", p).strip(" ,;")
    return p

def extract_parties_from_title(title: str) -> List[str]:
    """
    Heuristic: split on ' v ' or ' vs ' and return [partyA, partyB].
    Keep it conservative; store raw title always.
    """
    parts = VS_SPLIT_RE.split(title, maxsplit=1)
    if len(parts) != 2:
        return []
    left, right = map(normalize_party, parts)
    # Trim trailing citation blocks like "[2025] KESC 75..." if present
    right = re.sub(r"\[\d{4}\].*$", "", right).strip()
    return [left, right] if left and right else []

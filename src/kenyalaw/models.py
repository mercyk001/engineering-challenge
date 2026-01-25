from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List, Optional

@dataclass(frozen=True)
class DocumentRef:
    source: str               # e.g. "judgments"
    url: str                  # detail page URL
    doc_id: str               # stable ID derived from URL (canonical)

@dataclass
class DocumentRecord:
    doc_id: str
    source: str
    url: str
    title: str
    raw_text: str

    # Optional enrichments
    metadata: Dict[str, Any] = field(default_factory=dict)
    parties: List[str] = field(default_factory=list)

    pdf_url: Optional[str] = None
    docx_url: Optional[str] = None
    pdf_path: Optional[str] = None

    fetched_at: datetime = field(default_factory=datetime.utcnow)
    checksum: Optional[str] = None

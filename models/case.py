from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


def _parse_datetime(value: Union[str, datetime, None]) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        s = value.strip()
        try:
            return datetime.fromisoformat(s)
        except Exception:
            pass
        for fmt in ("%Y-%m-%d", "%d %B %Y", "%d %b %Y", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                continue
    logger.debug("Unable to parse date value %r", value)
    return None


@dataclass
class Case:
    case_id: str
    title: str
    citation: Optional[str] = ""
    court: Optional[str] = ""
    judge: List[str] = field(default_factory=list)
    judgement_date: Optional[datetime] = None
    parties: Dict[str, Any] = field(default_factory=dict)
    summary: Optional[str] = ""
    url: Optional[str] = ""
    pdf_url: Optional[str] = None
    raw_text: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not isinstance(self.judgement_date, (type(None), datetime)):
            parsed = _parse_datetime(self.judgement_date)  
            if parsed is None:
                logger.warning("Case %s: judgement_date %r could not be parsed", self.case_id, self.judgement_date)
                self.judgement_date = None
            else:
                self.judgement_date = parsed

        if self.judge is None:
            self.judge = []
        elif isinstance(self.judge, str):
            self.judge = [j.strip() for j in self.judge.split(",") if j.strip()]

        if self.parties is None:
            self.parties = {}

    def to_dict(self, include_none: bool = False) -> Dict[str, Any]:
        d = asdict(self)
        if isinstance(d.get("judgement_date"), datetime):
            d["judgement_date"] = d["judgement_date"].isoformat()
        else:
            d["judgement_date"] = None if d.get("judgement_date") is None else str(d.get("judgement_date"))

        if isinstance(d.get("scraped_at"), datetime):
            d["scraped_at"] = d["scraped_at"].isoformat()

        if not include_none:
            d = {k: v for k, v in d.items() if v is not None and v != ""}

        d["id"] = d.get("case_id")
        return d

    def to_json(self, **json_kwargs) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str, **json_kwargs)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Case":
        payload = dict(data)
        if "case_id" not in payload and "id" in payload:
            payload["case_id"] = payload.pop("id")
        if "judgement_date" in payload:
            payload["judgement_date"] = _parse_datetime(payload["judgement_date"])
        return cls(
            case_id=payload.get("case_id", ""),
            title=payload.get("title", ""),
            citation=payload.get("citation", ""),
            court=payload.get("court", ""),
            judge=payload.get("judge", []) or [],
            judgement_date=payload.get("judgement_date"),
            parties=payload.get("parties", {}) or {},
            summary=payload.get("summary", ""),
            url=payload.get("url", ""),
            pdf_url=payload.get("pdf_url"),
            raw_text=payload.get("raw_text"),
        )

    def validate(self) -> List[str]:
        errors = []
        if not self.case_id:
            errors.append("case_id is required")
        if not self.title:
            errors.append("title is required")
        return errors
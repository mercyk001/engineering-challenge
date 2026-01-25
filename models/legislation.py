from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


@dataclass
class Legislation:
    act_id: str
    title: str
    chapter: Optional[str] = None
    year: Optional[int] = None
    download_url: Optional[str] = None
    last_revision_date: Optional[str] = None
    category: Optional[str] = None
    raw_text: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if isinstance(d.get("scraped_at"), datetime):
            d["scraped_at"] = d["scraped_at"].isoformat()
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)
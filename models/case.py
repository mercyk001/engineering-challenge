from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class Case:
    case_id: str
    title: str
    citation: str
    court: str
    judge: List[str]
    judgement_date: str
    parties: dict
    summary: str
    url: str
    pdf_url: Optional[str] = None
    raw_text: Optional[str] = None
    
    
    def to_dict(self):
        return {
            "id": self.case_id,
            "title": self.title,
            "citation": self.citation,
            "court": self.court,    
            "judge": self.judge,
            "judgement_date": self.judgement_date,
            "parties": self.parties,
            "summary": self.summary,
            "url": self.url,
            "pdf_url": self.pdf_url,
            "raw_text": self.raw_text,
            "scraped_at": datetime.utcnow().isoformat()
        }
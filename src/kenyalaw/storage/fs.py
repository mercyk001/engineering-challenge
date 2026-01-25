from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import hashlib

@dataclass
class FileStore:
    root: Path

    def pdf_path(self, doc_id: str) -> Path:
        return self.root / "pdfs" / f"{doc_id}.pdf"

    def write_bytes_if_missing(self, path: Path, content: bytes) -> str:
        path.parent.mkdir(parents=True, exist_ok=True)
        sha = hashlib.sha256(content).hexdigest()
        if path.exists() and path.stat().st_size > 0:
            return sha
        path.write_bytes(content)
        return sha

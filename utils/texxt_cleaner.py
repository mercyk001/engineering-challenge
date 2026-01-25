import re
import html
from typing import Optional


def clean_whitespace(text: Optional[str]) -> str:
    if not text:
        return ""
    # unescape entities, normalize whitespace
    t = html.unescape(text)
    t = re.sub(r"\r\n|\r", "\n", t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{2,}", "\n\n", t)
    return t.strip()
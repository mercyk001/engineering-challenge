import re
import unicodedata
from typing import Optional


def slugify(value: str, max_length: int = 64) -> str:
    value = str(value)
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    value = re.sub(r"[-\s]+", "_", value)
    return value[:max_length]


def ensure_list(val):
    if val is None:
        return []
    if isinstance(val, list):
        return val
    return [val]
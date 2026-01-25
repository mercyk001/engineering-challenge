from typing import Protocol, Dict, Any, Optional


class DatabaseInterface(Protocol):
    def insert(self, table: str, payload: Dict[str, Any]) -> Optional[str]:
        ...

    def find(self, table: str, query: Dict[str, Any]):
        ...
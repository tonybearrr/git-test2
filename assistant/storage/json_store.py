from __future__ import annotations
import json
import os
from typing import Any, Dict, Iterable, List, Optional

from assistant.utils.io import atomic_write_json, ensure_directory


class JSONStorage:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        ensure_directory(os.path.dirname(self.file_path))
        if not os.path.exists(self.file_path):
            atomic_write_json(self.file_path, {})

    def load(self) -> Dict[str, Any]:
        if not os.path.exists(self.file_path):
            return {}
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
            return {}
        except Exception:
            return {}

    def save(self, data: Dict[str, Any]) -> None:
        atomic_write_json(self.file_path, data)

    def all(self) -> Dict[str, Any]:
        return self.load()

    def get(self, entity_id: str) -> Optional[Dict[str, Any]]:
        return self.load().get(entity_id)

    def upsert(self, entity_id: str, entity: Dict[str, Any]) -> None:
        data = self.load()
        data[entity_id] = entity
        self.save(data)

    def delete(self, entity_id: str) -> bool:
        data = self.load()
        if entity_id in data:
            del data[entity_id]
            self.save(data)
            return True
        return False

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from assistant.utils.validation import split_tags


@dataclass
class Note:
    id: str
    text: str
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds") + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds") + "Z")

    def validate(self) -> None:
        if not self.text or not self.text.strip():
            raise ValueError("Note text cannot be empty")
        self.tags = [t for t in self.tags if t]

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "text": self.text,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def new(cls, text: str, tags_text: Optional[str] = None) -> "Note":
        now = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        instance = cls(
            id=str(uuid4()),
            text=text.strip(),
            tags=split_tags(tags_text),
            created_at=now,
            updated_at=now,
        )
        instance.validate()
        return instance

    @classmethod
    def from_dict(cls, data: Dict) -> "Note":
        instance = cls(
            id=data.get("id"),
            text=data.get("text", ""),
            tags=list(data.get("tags") or []),
            created_at=data.get("created_at") or datetime.utcnow().isoformat(timespec="seconds") + "Z",
            updated_at=data.get("updated_at") or datetime.utcnow().isoformat(timespec="seconds") + "Z",
        )
        # Validate lazily when editing/saving
        return instance

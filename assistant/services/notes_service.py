from __future__ import annotations
from dataclasses import asdict
from datetime import datetime
from typing import Dict, List, Optional

from assistant.models.note import Note
from assistant.storage.json_store import JSONStorage


class NotesService:
    def __init__(self, storage: JSONStorage) -> None:
        self.storage = storage

    def list_notes(self, sort_by: str = "created") -> List[Dict]:
        notes = [Note.from_dict(v) for v in self.storage.all().values()]
        if sort_by == "updated":
            notes.sort(key=lambda n: n.updated_at, reverse=True)
        elif sort_by == "text":
            notes.sort(key=lambda n: n.text.lower())
        elif sort_by == "tags":
            notes.sort(key=lambda n: ",".join(n.tags).lower())
        else:
            notes.sort(key=lambda n: n.created_at, reverse=True)
        return [n.to_dict() for n in notes]

    def add_note(self, text: str, tags_text: Optional[str] = None) -> Dict:
        note = Note.new(text=text, tags_text=tags_text)
        self.storage.upsert(note.id, note.to_dict())
        return note.to_dict()

    def search_notes(self, query: str) -> List[Dict]:
        q = query.strip().lower()
        results: List[Note] = []
        for data in self.storage.all().values():
            n = Note.from_dict(data)
            haystack = " ".join([n.text or "", ",".join(n.tags or [])]).lower()
            if q in haystack:
                results.append(n)
        results.sort(key=lambda n: n.updated_at, reverse=True)
        return [n.to_dict() for n in results]

    def search_by_tags(self, tags: List[str]) -> List[Dict]:
        tags_lower = {t.strip().lower() for t in tags if t.strip()}
        results: List[Note] = []
        for data in self.storage.all().values():
            n = Note.from_dict(data)
            note_tags = {t.lower() for t in (n.tags or [])}
            if tags_lower.issubset(note_tags):
                results.append(n)
        results.sort(key=lambda n: n.updated_at, reverse=True)
        return [n.to_dict() for n in results]

    def edit_note(self, note_id: str, **fields: str) -> Optional[Dict]:
        raw = self.storage.get(note_id)
        if not raw:
            return None
        note = Note.from_dict(raw)
        changed = False
        if (text := fields.get("text")) is not None:
            note.text = text.strip()
            changed = True
        if (tags := fields.get("tags")) is not None:
            tag_list = [t.strip() for t in tags.split(",") if t.strip()]
            note.tags = tag_list
            changed = True
        if changed:
            note.validate()
            note.updated_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
            self.storage.upsert(note.id, note.to_dict())
        return note.to_dict()

    def delete_note(self, note_id: str) -> bool:
        return self.storage.delete(note_id)

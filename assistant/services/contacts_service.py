from __future__ import annotations
from dataclasses import asdict
from datetime import date
from typing import Dict, List, Optional

from assistant.models.contact import Contact
from assistant.storage.json_store import JSONStorage
from assistant.utils.dates import days_until_next_birthday, parse_date


class ContactsService:
    def __init__(self, storage: JSONStorage) -> None:
        self.storage = storage

    def list_contacts(self) -> List[Dict]:
        data = self.storage.all()
        contacts = [Contact.from_dict(v) for v in data.values()]
        contacts.sort(key=lambda c: c.name.lower())
        return [c.to_dict() for c in contacts]

    def add_contact(
        self,
        name: str,
        address: Optional[str] = None,
        phones: Optional[List[str]] = None,
        email: Optional[str] = None,
        birthday: Optional[str] = None,
    ) -> Dict:
        contact = Contact.new(name=name, address=address, phones=phones, email=email, birthday=birthday)
        self.storage.upsert(contact.id, contact.to_dict())
        return contact.to_dict()

    def search_contacts(self, query: str) -> List[Dict]:
        q = query.strip().lower()
        results: List[Contact] = []
        for data in self.storage.all().values():
            c = Contact.from_dict(data)
            haystack = " ".join([
                c.name or "",
                c.address or "",
                " ".join(c.phones or []),
                c.email or "",
                c.birthday or "",
            ]).lower()
            if q in haystack:
                results.append(c)
        results.sort(key=lambda c: c.name.lower())
        return [c.to_dict() for c in results]

    def edit_contact(self, contact_id: str, **fields: str) -> Optional[Dict]:
        raw = self.storage.get(contact_id)
        if not raw:
            return None
        contact = Contact.from_dict(raw)
        if (name := fields.get("name")) is not None:
            contact.name = name.strip()
        if (address := fields.get("address")) is not None:
            contact.address = address.strip() or None
        if (email := fields.get("email")) is not None:
            contact.email = email.strip() or None
        if (birthday := fields.get("birthday")) is not None:
            contact.birthday = birthday.strip() or None
        if (phones := fields.get("phones")) is not None:
            # phones expected as comma-separated string
            phone_list = [p.strip() for p in phones.split(",") if p.strip()]
            contact.phones = phone_list
        # Normalize and validate before save
        contact.normalize()
        contact.validate()
        self.storage.upsert(contact.id, contact.to_dict())
        return contact.to_dict()

    def delete_contact(self, contact_id: str) -> bool:
        return self.storage.delete(contact_id)

    def birthdays_in(self, days: int) -> List[Dict]:
        today = date.today()
        upcoming: List[Dict] = []
        for data in self.storage.all().values():
            c = Contact.from_dict(data)
            if not c.birthday:
                continue
            bday = parse_date(c.birthday)
            if not bday:
                continue
            days_until = days_until_next_birthday(bday, today)
            if 0 <= days_until <= days:
                item = c.to_dict()
                item["days_until_birthday"] = days_until
                upcoming.append(item)
        upcoming.sort(key=lambda x: (x.get("days_until_birthday", 0), x.get("name", "").lower()))
        return upcoming

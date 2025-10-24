from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import uuid4

from assistant.utils.validation import is_valid_email, is_valid_phone, normalize_phone
from assistant.utils.dates import parse_date, format_date


@dataclass
class Contact:
    id: str
    name: str
    address: Optional[str] = None
    phones: List[str] = field(default_factory=list)
    email: Optional[str] = None
    birthday: Optional[str] = None  # YYYY-MM-DD

    def validate(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Name is required for contact")
        if self.email and not is_valid_email(self.email):
            raise ValueError("Invalid email address")
        for phone in self.phones:
            if not is_valid_phone(phone):
                raise ValueError(f"Invalid phone number: {phone}")
        # Validate birthday format if provided
        if self.birthday and not parse_date(self.birthday):
            raise ValueError("Birthday must be in YYYY-MM-DD format")

    def normalize(self) -> None:
        self.phones = [normalize_phone(p) for p in self.phones if p]
        # No extra normalization for birthday/email beyond validation

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "phones": self.phones,
            "email": self.email,
            "birthday": self.birthday,
        }

    @classmethod
    def new(
        cls,
        name: str,
        address: Optional[str] = None,
        phones: Optional[List[str]] = None,
        email: Optional[str] = None,
        birthday: Optional[str] = None,
    ) -> "Contact":
        instance = cls(
            id=str(uuid4()),
            name=name.strip(),
            address=address.strip() if address else None,
            phones=[p for p in (phones or []) if p],
            email=email.strip() if email else None,
            birthday=birthday.strip() if birthday else None,
        )
        instance.normalize()
        instance.validate()
        return instance

    @classmethod
    def from_dict(cls, data: Dict) -> "Contact":
        instance = cls(
            id=data.get("id"),
            name=data.get("name", ""),
            address=data.get("address"),
            phones=list(data.get("phones") or []),
            email=data.get("email"),
            birthday=data.get("birthday"),
        )
        instance.normalize()
        # Do not validate strictly on load to tolerate legacy data; validate on save
        return instance

import re
from typing import Iterable, List, Optional


_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def is_valid_email(email: Optional[str]) -> bool:
    if email is None or email == "":
        return True
    return _EMAIL_RE.match(email) is not None


def normalize_phone(raw_phone: str) -> str:
    cleaned = raw_phone.strip()
    # Keep leading plus if present, strip other non-digit characters
    leading_plus = cleaned.startswith("+")
    digits_only = re.sub(r"[^0-9]", "", cleaned)
    if leading_plus:
        return "+" + digits_only
    return digits_only


def is_valid_phone(phone: Optional[str]) -> bool:
    if phone is None or phone == "":
        return True
    normalized = normalize_phone(phone)
    # Must be digits with optional leading + and total length reasonable
    digits = normalized[1:] if normalized.startswith("+") else normalized
    return 7 <= len(digits) <= 15


def split_tags(tags_text: Optional[str]) -> List[str]:
    if not tags_text:
        return []
    tags = [tag.strip() for tag in tags_text.split(",")]
    return [t for t in tags if t]

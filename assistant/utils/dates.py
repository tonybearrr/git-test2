from __future__ import annotations
from datetime import date, datetime, timedelta
from typing import Optional


_DATE_FMT = "%Y-%m-%d"


def parse_date(date_text: Optional[str]) -> Optional[date]:
    if not date_text:
        return None
    try:
        return datetime.strptime(date_text, _DATE_FMT).date()
    except Exception:
        return None


def format_date(d: Optional[date]) -> Optional[str]:
    if d is None:
        return None
    return d.strftime(_DATE_FMT)


def days_until_next_birthday(birthday: date, today: Optional[date] = None) -> int:
    if today is None:
        today = date.today()
    # Next birthday this year
    try:
        next_bday = birthday.replace(year=today.year)
    except ValueError:
        # Handle Feb 29 on non-leap year -> use Feb 28
        next_bday = date(today.year, 2, 28)
    if next_bday < today:
        try:
            next_bday = birthday.replace(year=today.year + 1)
        except ValueError:
            next_bday = date(today.year + 1, 2, 28)
    return (next_bday - today).days


def add_days(d: date, days: int) -> date:
    return d + timedelta(days=days)

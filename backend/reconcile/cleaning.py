"""Pure cleaning helpers (no Django). Tested in tests/test_cleaning.py."""
import re
from decimal import Decimal, InvalidOperation


def normalize_ref(raw):
    """'rec1034', ' REC - 1070 ', '1112' -> 'REC-1034' etc. None if no digits."""
    m = re.search(r"\d+", raw or "")
    return f"REC-{m.group()}" if m else None


def parse_amount(raw):
    """'1,25,400.00' -> Decimal('125400.00'). Blank/junk -> None (unknown), never 0."""
    s = (raw or "").strip().replace(",", "")
    if not s:
        return None
    try:
        return Decimal(s)
    except InvalidOperation:
        return None

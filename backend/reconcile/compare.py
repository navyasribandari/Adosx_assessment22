"""Pure comparison logic: no database, no web code.

a_rows: {record_id: {'total': Decimal, 'location': str, 'date': str, 'state': str}}
b_rows: [{'entry_id', 'ref' (already cleaned), 'value': Decimal|None, 'location', 'date'}]

Returns a list of dicts: reason, record_id, a_location, b_location, a_value, b_value, entry_ids.
"""
from decimal import Decimal

MISSING_IN_B = "MISSING_IN_B"
ORPHAN_IN_B = "ORPHAN_IN_B"
DUPLICATE_IN_B = "DUPLICATE_IN_B"
VALUE_MISMATCH = "VALUE_MISMATCH"
LOCATION_MISMATCH = "LOCATION_MISMATCH"
DATE_MISMATCH = "DATE_MISMATCH"
VOIDED_IN_A = "VOIDED_IN_A"  # extra: A voided the record but B still has an entry

REASONS = [MISSING_IN_B, ORPHAN_IN_B, DUPLICATE_IN_B, VALUE_MISMATCH,
           LOCATION_MISMATCH, DATE_MISMATCH, VOIDED_IN_A]


def _row(reason, record_id, a=None, entries=(), b_value=None):
    return {
        "reason": reason,
        "record_id": record_id,
        "a_location": a["location"] if a else None,
        "b_location": entries[0]["location"] if entries else None,
        "a_value": a["total"] if a else None,
        "b_value": b_value,
        "entry_ids": [e["entry_id"] for e in entries],
    }


def compare(a_rows, b_rows):
    out, by_ref = [], {}
    for e in b_rows:
        by_ref.setdefault(e["ref"], []).append(e)

    # B entries whose reference is not an A record (or could not be parsed)
    for ref, entries in by_ref.items():
        if ref not in a_rows:
            for e in entries:
                out.append(_row(ORPHAN_IN_B, ref or e["entry_id"], None, [e], e["value"]))

    for rid, a in a_rows.items():
        entries = by_ref.get(rid, [])
        voided = a.get("state") == "VOIDED"
        if not entries:
            if not voided:  # a voided record with no B entry is expected
                out.append(_row(MISSING_IN_B, rid, a))
            continue
        if voided:
            out.append(_row(VOIDED_IN_A, rid, a, entries, entries[0]["value"]))
            continue
        vals = [e["value"] for e in entries]
        if any(v is None for v in vals):  # blank = unknown, not zero
            out.append(_row(VALUE_MISMATCH, rid, a, entries, None))
            continue
        if len(entries) > 1:
            total_b = sum(vals, Decimal("0"))
            if total_b != a["total"]:  # a split that adds up is fine
                out.append(_row(DUPLICATE_IN_B, rid, a, entries, total_b))
            continue  # location/date are not checked on multi-entry records
        e = entries[0]
        if e["value"] != a["total"]:
            out.append(_row(VALUE_MISMATCH, rid, a, entries, e["value"]))
        if e["location"] != a["location"]:
            out.append(_row(LOCATION_MISMATCH, rid, a, entries, e["value"]))
        if e["date"] != a["date"]:
            out.append(_row(DATE_MISMATCH, rid, a, entries, e["value"]))
    return out

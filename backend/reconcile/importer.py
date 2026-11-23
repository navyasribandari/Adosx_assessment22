"""CSV -> database. Every CSV row becomes exactly one DB row; bad fields become NULL."""
import csv
from datetime import date
from pathlib import Path

from .cleaning import normalize_ref, parse_amount
from .models import Location, SystemARecord, SystemBEntry


def _rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            yield {k.strip(): (v or "").strip() for k, v in row.items() if k}


def _date(s):
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


def import_all(data_dir):
    data_dir = Path(data_dir)
    stats = {"locations": 0, "a_read": 0, "a_saved": 0, "b_read": 0, "b_saved": 0,
             "values_left_empty": 0, "refs_cleaned": 0, "actor_null": 0}

    for r in _rows(data_dir / "locations.csv"):
        Location.objects.update_or_create(
            location_id=r["location_id"],
            defaults={"org_id": r["org_id"], "name": r.get("location_name", "")})
        stats["locations"] += 1

    locs = {l.location_id: l for l in Location.objects.all()}

    for r in _rows(data_dir / "system_a.csv"):
        stats["a_read"] += 1
        if not r["actor_id"]:
            stats["actor_null"] += 1
        SystemARecord.objects.update_or_create(
            record_id=r["record_id"],
            defaults={
                "location": locs[r["location_id"]],
                "event_date": _date(r["event_date"]),
                "category_code": r["category_code"],
                "actor_id": r["actor_id"] or None,
                "base_value": parse_amount(r["base_value"]),
                "adjustment": parse_amount(r["adjustment"]),
                "total_value": parse_amount(r["total_value"]),
                "state": r["state"],
            })
        stats["a_saved"] += 1

    for r in _rows(data_dir / "system_b.csv"):
        stats["b_read"] += 1
        ref = normalize_ref(r["record_ref"])
        if ref != r["record_ref"]:
            stats["refs_cleaned"] += 1
        value = parse_amount(r["value"])
        if value is None:
            stats["values_left_empty"] += 1
        SystemBEntry.objects.update_or_create(
            entry_id=r["entry_id"],
            defaults={
                "record_ref_raw": r["record_ref"],
                "record_ref": ref,
                "location": locs[r["location_id"]],
                "recorded_on": _date(r["recorded_on"]),
                "value_raw": r["value"],
                "value": value,
                "label": r["label"],
            })
        stats["b_saved"] += 1
    return stats

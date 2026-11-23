"""DB -> compare() glue. Tenant scoping happens in the queries here."""
from django.db.models import Q

from .compare import compare
from .models import Location, SystemARecord, SystemBEntry


def disagreements_for_org(org):
    # A side: only records at this org's locations (org comes from Location, never from IDs).
    a_qs = SystemARecord.objects.filter(location__org_id=org).select_related("location")
    a_rows = {
        a.record_id: {"total": a.total_value, "location": a.location.location_id,
                      "date": a.event_date, "state": a.state}
        for a in a_qs
    }
    # B side: entries at this org's locations, plus entries pointing at this org's A records
    # (the cross-org row: B put it at another org's location).
    b_qs = SystemBEntry.objects.filter(
        Q(location__org_id=org) | Q(record_ref__in=list(a_rows))).select_related("location")
    b_rows, b_org = [], {}
    for e in b_qs:
        b_rows.append({"entry_id": e.entry_id, "ref": e.record_ref, "value": e.value,
                       "location": e.location.location_id, "date": e.recorded_on})
        b_org[e.location.location_id] = e.location.org_id

    out = []
    for r in compare(a_rows, b_rows):
        # Never reveal another org's location: hide it, keep the row.
        r["b_location_hidden"] = bool(r["b_location"]) and b_org.get(r["b_location"]) != org
        if r["b_location_hidden"]:
            r["b_location"] = None
        out.append(r)
    return out


def org_exists(org):
    return Location.objects.filter(org_id=org).exists()

import json
from pathlib import Path

import pytest
from django.conf import settings

from reconcile.importer import import_all

pytestmark = pytest.mark.django_db
DATA = Path(settings.BASE_DIR) / "data"


@pytest.fixture(autouse=True)
def loaded():
    import_all(DATA)


def get(client, **params):
    res = client.get("/api/disagreements/", params)
    return res.status_code, json.loads(res.content)


def test_importer_loses_no_rows_and_is_idempotent():
    from reconcile.models import SystemARecord, SystemBEntry
    import_all(DATA)
    assert SystemARecord.objects.count() == 120
    assert SystemBEntry.objects.count() == 121
    assert SystemBEntry.objects.filter(value__isnull=True).count() == 1
    assert SystemARecord.objects.filter(actor_id__isnull=True).count() == 1


@pytest.mark.parametrize("org,other_prefix", [("ORG-A", "LOC-2"), ("ORG-B", "LOC-1")])
def test_org_never_sees_other_orgs_locations(client, org, other_prefix):
    status, body = get(client, org=org)
    assert status == 200 and body["count"] > 0
    for r in body["results"]:
        for k in ("location", "a_location", "b_location"):
            assert not (r[k] or "").startswith(other_prefix), r


def test_org_a_sees_cross_org_row_without_org_b_location(client):
    _, body = get(client, org="ORG-A", reason="LOCATION_MISMATCH")
    row = [r for r in body["results"] if r["record_id"] == "REC-1077"][0]
    assert row["a_location"] == "LOC-102"
    assert row["b_location"] is None and row["b_location_hidden"] is True


def test_org_b_does_not_see_org_a_record(client):
    _, body = get(client, org="ORG-B")
    assert all(r["location"] != "LOC-102" for r in body["results"])


def test_org_is_required_and_validated(client):
    assert get(client)[0] == 400
    assert get(client, org="ORG-Z")[0] == 404


def test_real_data_findings(client):
    _, body = get(client, org="ORG-A")
    _, body_b = get(client, org="ORG-B")
    found = {(r["reason"], r["record_id"]) for r in body["results"] + body_b["results"]}
    assert ("MISSING_IN_B", "REC-1015") in found
    assert ("DUPLICATE_IN_B", "REC-1042") in found
    assert ("VALUE_MISMATCH", "REC-1050") in found
    assert ("ORPHAN_IN_B", "REC-1999") in found
    assert not any(rid == "REC-1055" for _, rid in found)  # split: fine

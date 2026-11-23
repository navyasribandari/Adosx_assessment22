from decimal import Decimal as D

from reconcile.cleaning import normalize_ref, parse_amount
from reconcile.compare import compare


def a_rec(total="100.00", loc="L1", date="2026-03-01", state="CONFIRMED"):
    return {"total": D(total), "location": loc, "date": date, "state": state}


def entry(eid, ref="REC-1", value="100.00", loc="L1", date="2026-03-01"):
    return {"entry_id": eid, "ref": ref, "value": None if value is None else D(value),
            "location": loc, "date": date}


def reasons(result):
    return [r["reason"] for r in result]


def test_clean_row_has_no_disagreement():
    assert compare({"REC-1": a_rec()}, [entry("E1")]) == []


def test_missing_in_b():
    assert reasons(compare({"REC-1": a_rec()}, [])) == ["MISSING_IN_B"]


def test_orphan_in_b():
    res = compare({"REC-1": a_rec()}, [entry("E1"), entry("E2", ref="REC-999")])
    assert reasons(res) == ["ORPHAN_IN_B"]
    assert res[0]["entry_ids"] == ["E2"]


def test_duplicate_same_amount_is_flagged():
    res = compare({"REC-1": a_rec()}, [entry("E1"), entry("E2")])
    assert reasons(res) == ["DUPLICATE_IN_B"]


def test_split_that_sums_is_not_an_error():
    b = [entry("E1", value="40.00"), entry("E2", value="60.00")]
    assert compare({"REC-1": a_rec()}, b) == []


def test_split_that_does_not_sum_is_flagged():
    b = [entry("E1", value="40.00"), entry("E2", value="50.00")]
    assert reasons(compare({"REC-1": a_rec()}, b)) == ["DUPLICATE_IN_B"]


def test_value_mismatch():
    res = compare({"REC-1": a_rec()}, [entry("E1", value="90.00")])
    assert reasons(res) == ["VALUE_MISMATCH"]


def test_b_equal_to_base_not_total_is_mismatch():
    # A total is base+adjustment; B holding only the base amount is wrong
    res = compare({"REC-1": a_rec(total="121.00")}, [entry("E1", value="94.00")])
    assert reasons(res) == ["VALUE_MISMATCH"]


def test_blank_value_flagged_and_not_zero():
    res = compare({"REC-1": a_rec()}, [entry("E1", value=None)])
    assert reasons(res) == ["VALUE_MISMATCH"]
    assert res[0]["b_value"] is None


def test_blank_value_not_treated_as_zero_even_when_total_is_zero():
    res = compare({"REC-1": a_rec(total="0.00")}, [entry("E1", value=None)])
    assert reasons(res) == ["VALUE_MISMATCH"]


def test_location_mismatch():
    res = compare({"REC-1": a_rec()}, [entry("E1", loc="L2")])
    assert reasons(res) == ["LOCATION_MISMATCH"]


def test_date_mismatch():
    res = compare({"REC-1": a_rec()}, [entry("E1", date="2026-03-03")])
    assert reasons(res) == ["DATE_MISMATCH"]


def test_voided_without_b_entry_is_expected():
    assert compare({"REC-1": a_rec(state="VOIDED")}, []) == []


def test_voided_with_b_entry_is_flagged():
    res = compare({"REC-1": a_rec(state="VOIDED")}, [entry("E1")])
    assert reasons(res) == ["VOIDED_IN_A"]


def test_messy_references_match_and_are_not_flagged():
    a = {"REC-1034": a_rec(), "REC-1070": a_rec(), "REC-1112": a_rec()}
    refs = [normalize_ref("rec1034"), normalize_ref(" REC - 1070 "), normalize_ref("1112")]
    assert refs == ["REC-1034", "REC-1070", "REC-1112"]
    b = [entry(f"E{i}", ref=r) for i, r in enumerate(refs)]
    assert compare(a, b) == []


def test_indian_comma_amount_equals_plain_amount():
    assert parse_amount("1,25,400.00") == D("125400.00")
    res = compare({"REC-1": a_rec(total="125400.00")}, [entry("E1", value=str(parse_amount("1,25,400.00")))])
    assert res == []


def test_parse_amount_blank_and_junk_are_none_not_zero():
    assert parse_amount("") is None
    assert parse_amount("   ") is None
    assert parse_amount("abc") is None
    assert parse_amount(None) is None


def test_normalize_ref_without_digits_is_none():
    assert normalize_ref("") is None
    assert normalize_ref("n/a") is None

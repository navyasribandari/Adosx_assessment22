# Decisions

## Decision: compare B's value with A's total_value
-Rejected: compare with base_value
-Why: B equals total_value (base + adjustment) on almost every row; REC-1003, REC-1027 and REC-1088 hold only the base amount in B, which is a real mismatch.

## Decision: blank B value is NULL (unknown), flagged as VALUE_MISMATCH
-Rejected: treating blank as 0
-Why: 0 is a real amount; unknown must never equal or differ by a made-up number. The raw text is kept in value_raw.

## Decision: clean references with the first run of digits -> REC-<n>
-Rejected: exact string match on record_ref
-Why: rec1034, " REC - 1070 " and 1112 clearly mean the same records; the raw text is kept in record_ref_raw.

## Decision: two B entries are a split only if they sum exactly to A's total
-Rejected: flagging every record with 2+ entries
-Why: REC-1055 (40/60-style "part 2 of 2") is legitimate; REC-1042 (same amount twice) is a duplicate. Splits that do not sum are also flagged.

## Decision: VOIDED in A with a B entry is flagged (VOIDED_IN_A); VOIDED with no B entry is expected
-Rejected: silently accepting the B entry, or flagging MISSING_IN_B for voided records
-Why: B still counting a record A voided is a real disagreement; a voided record needing no B entry is not.

## Decision: add DATE_MISMATCH and LOCATION_MISMATCH (extras)
-Rejected: ignoring them
-Why: the data has deliberate date and location differences (REC-1009, REC-1077); a reconciliation should surface them.

## Decision: cross-org row (REC-1077: A at LOC-102, B at LOC-201)
-Rejected: showing "A says LOC-102, B says LOC-201" to ORG-A
-Why: ORG-A sees the row with B's location hidden; ORG-B sees B's entry only as ORPHAN_IN_B at its own location and never sees A's record. B's amount is still shown to ORG-A (it describes ORG-A's record).

## Decision: tenant filtering inside DB queries, org derived only from locations.csv
-Rejected: filtering in the frontend or inferring org from LOC-1xx/2xx
-Why: hidden data is still leaked data in the network tab.

## Decision: Django + SQLite + Decimal, plain Django template with vanilla JS instead of React
-Rejected: React/Vite, floats, DRF
-Why: one page and one endpoint; fewer moving parts to explain. Decimal for exact money compares.

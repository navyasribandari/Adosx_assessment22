from django.http import JsonResponse
from django.shortcuts import render

from .compare import REASONS
from .services import disagreements_for_org, org_exists


def index(request):
    return render(request, "reconcile/index.html", {"reasons": REASONS})


def _s(v):
    return None if v is None else str(v)


def disagreements(request):
    org = request.GET.get("org")
    if not org:
        return JsonResponse({"error": "org is required"}, status=400)
    if not org_exists(org):
        return JsonResponse({"error": "unknown org"}, status=404)

    rows = disagreements_for_org(org)
    reason = request.GET.get("reason")
    if reason:
        rows = [r for r in rows if r["reason"] == reason]

    sort = request.GET.get("sort", "")
    if sort in ("value", "-value"):
        def key(r):
            v = r["a_value"] if r["a_value"] is not None else r["b_value"]
            return v
        known = [r for r in rows if key(r) is not None]
        unknown = [r for r in rows if key(r) is None]  # empty values always last
        known.sort(key=key, reverse=sort.startswith("-"))
        rows = known + unknown

    data = []
    for r in rows:
        diff = (r["b_value"] - r["a_value"]
                if r["a_value"] is not None and r["b_value"] is not None else None)
        data.append({"reason": r["reason"], "record_id": r["record_id"],
                     "location": r["a_location"] or r["b_location"],
                     "a_location": r["a_location"], "b_location": r["b_location"],
                     "b_location_hidden": r["b_location_hidden"],
                     "a_value": _s(r["a_value"]), "b_value": _s(r["b_value"]),
                     "difference": _s(diff)})
    return JsonResponse({"org": org, "count": len(data), "results": data})

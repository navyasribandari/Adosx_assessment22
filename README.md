# DealerOS reconciliation

Django + SQLite backend, plain Django-template page (vanilla JS) for the table. No React, see DECISIONS.

## Run from a clean clone
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd backend
python manage.py makemigrations reconcile
python manage.py migrate
python manage.py import_data      # run twice: same counts, no duplicates
python manage.py runserver        # open http://127.0.0.1:8000/
pytest                            # from backend/
```
Expected import summary: `A: 120 read, 120 saved; B: 121 read, 121 saved; values left empty: 1; refs cleaned: 3`.

## What I built
Importer (nothing dropped, bad values NULL, raw text kept), pure comparison function (`reconcile/compare.py`),
`GET /api/disagreements/?org=ORG-A&reason=...&sort=-value`, a table page, tests.

## Deliberately not built
Auth, pagination, Docker, CSS, React.

## How I worked with the agent
TODO (write in your own words): which agent, what you asked, what you wrote yourself, how you checked it.

## Three questions
a. TODO: one real thing the agent got wrong and the check that caught it.
b. TODO: the part you are least confident about (suggestion: the cross-org row / VOIDED handling).
c. TODO: what you would fix first with a second day.

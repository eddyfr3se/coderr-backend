# Setup check results

## Day 2 – 22 October 2026

The following checks were actually executed against the local setup:

| Check | Result |
| --- | --- |
| `python manage.py check` | No system check issues. |
| `python manage.py makemigrations --check --dry-run` | No changes detected. |
| `python manage.py migrate --check` | Completed successfully; no pending migrations. |
| `python -m pip check` | No broken requirements. |
| HTTP GET `http://127.0.0.1:8001/admin/login/` | 200. This checks the login page, not an authenticated admin session. |
| HTTP GET `http://127.0.0.1:5501/` | 200. |
| Backend response to frontend Origin header | Access-Control-Allow-Origin matched `http://127.0.0.1:5501`. |
| Served frontend configuration | API_BASE_URL and STATIC_BASE_URL both pointed to port 8001. |
| Browser start page at port 5501 | Coderr heading and navigation visible. Missing-data error visible because API features are not implemented. |
| `git check-ignore` | Confirmed exclusion of .env, .venv, db.sqlite3 and both local planning files. |
| `git remote -v` during setup | Initially no remote configured; origin was added later for the GitHub upload. |
| Listening ports | KanMind still on 8000/5500; Coderr on 8001/5501. |

HTTP checks used Python's standard-library urllib locally. The browser check
used a browser. These are setup checks, not Postman or
automated DRF business-function tests. No official Academy PM collection was
run. Registration, login, guest accounts, permissions, uploads and CRUD flows
have not been tested because those features are not implemented yet.

A fresh installation from an independent clone has not been performed.

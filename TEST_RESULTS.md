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

## Day 3 – Automated admin access checks, 23 October 2026

Initial teaching run: `python manage.py test core.tests --verbosity 1`.
Three tests ran; two passed and one deliberately failed because the login
page returned HTTP 200 while the assertion expected HTTP 201. Only the wrong
test expectation was corrected; no application behavior was changed.

Final run: `python manage.py test --verbosity 2`.

| Test | Result |
| --- | --- |
| Public GET of admin login page | HTTP 200; passed. |
| Anonymous GET of admin index | Redirect to admin login with next parameter; passed. |
| Staff GET of admin index using prepared session | HTTP 200; passed. |

All three tests passed. Django used an in-memory SQLite test database and
removed it afterwards. The SHA-256 of the local db.sqlite3 file matched
before and after the final run. The Django system check reported no issues.

These checks exercise Django's admin pages using APITestCase's HTTP client.
They do not establish Coderr API behavior, password login, token handling,
customer/business permissions, frontend workflows or official PM results.

The same three tests were also started manually in the Antigravity terminal
with `.venv/bin/python manage.py test`. The visible result was
`Ran 3 tests in 0.019s`, followed by `OK` and test database cleanup.

## Day 4 – Profile creation in admin, 29 October 2026

- Applied auth_app.0001_initial successfully; migration check found no missing
  model changes at that point.
- Signed-in admin pages initially used the old server process. Restarted only
  Coderr on port 8001 with automatic reloading enabled.
- Opened User profiles in the browser and confirmed the search field and
  Customer/Business filter were present.
- Created fictional local user profiltest_customer through Django without a
  usable password, then created its Customer profile through the browser admin.
  Left optional fields and file empty. The success message and saved row were
  visible, including the automatically populated creation date.
- Read the saved profile through the ORM: user association, customer type,
  empty text fields, empty file, creation timestamp and string representation
  matched expectations. The fictional user has no usable password.

This checks a model/admin workflow. No Coderr API endpoint or Postman request
was tested. The fixture remains in the local ignored database.

### Model tests and regression

Executed `python manage.py test --verbosity 1`: all nine tests passed
(the three existing admin tests and six new profile model tests).

New checks:

- Customer and Business pass explicit model validation.
- An unknown role raises ValidationError during full_clean.
- Optional text fields round-trip as empty strings; file is empty,
  creation timestamp exists and string representation shows the username.
- A second profile for the same user fails explicit uniqueness validation.
- Deleting a user removes its profile.
- Deleting a profile preserves its user.

The runner created and removed its separate test database. These validation
tests call full_clean explicitly; they do not claim that save automatically
validates choices. The duplicate check covers model validation rather than
an attempted database constraint violation.

`makemigrations --check --dry-run` reported no changes and `migrate --check`
completed successfully. No Coderr API/PM/Postman result is claimed.

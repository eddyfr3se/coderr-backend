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

## Day 5 – Registration and login, 2 November 2026

### Automated API tests

Executed `python manage.py test --verbosity 1`: **21 test methods passed**.
The twelve new methods cover registration for both profile types, response
fields and stored tokens, password hashing, mismatch handling, duplicate
usernames/emails, invalid roles/emails, required fields, login token reuse,
wrong passwords, unknown/inactive users and unsupported GET methods.
The test runner created and removed a separate test database.

### Postman desktop Collection Runner

Imported `postman/coderr-day5-auth.postman_collection.json` using the desktop
app's Import dialog and ran all requests with one iteration. Selected
No Environment, disabled Keep variable values and enabled running without
stored cookies. The visible run started at 11:41:18 on 2 November 2026.

| Requests | Assertions | Passed | Failed | Skipped | Execution errors |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 18 | 82 | 82 | 0 | 0 | 0 |

- Customer and Business registration returned 201 with documented fields.
- Both logins returned 200 and reused their registration tokens.
- Wrong password, unknown username, email in place of username, password
  mismatch, duplicate username/email, invalid role/email, missing fields and
  empty inputs returned controlled 400 errors.
- GET requests to the two POST-only endpoints returned 405.
- Assertions checked JSON, exact successful response fields, ID/token types,
  expected account data and absence of password fields.

This result was observed in the Postman desktop app, not produced by a CLI
runner or the official Academy PM suite. The committed collection has empty
runtime values and generates fictional credentials at execution time. Its
contents were imported unchanged for this run.

The two fictional accounts with suffix 1793616078463_74356 remain locally.
An ORM read confirmed their customer/business profiles and stored tokens,
with is_staff/is_superuser both false. No account cleanup endpoint exists yet.
No personal credentials or actual tokens are included in repository files.

Complete frontend browser flows, official PM tests and using tokens against
protected business endpoints remain unverified. No broader coverage is claimed.

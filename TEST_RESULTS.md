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

## Day 6 – Profile detail and permissions, 4 November 2026

Executed `python manage.py test --verbosity 1`: **30 test methods passed**.
Nine additional methods check partial serializer updates, email uniqueness,
authenticated reads, owner updates, rejected anonymous/foreign updates,
missing profiles and unsupported methods. Tests use a separate test database.

Imported `postman/coderr-day6-profiles.postman_collection.json` into the
Postman desktop app and ran all 15 requests with one iteration, No Environment,
Keep variable values disabled and stored cookies disabled. The visible run
started at 15:29:25 on 4 November 2026 and took 956 ms.

| Requests | Assertions | Passed | Failed | Skipped | Execution errors |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 15 | 51 | 51 | 0 | 0 | 0 |

Verified exact profile fields, empty optional text, reading another profile,
saved partial changes, rejected foreign changes (403), anonymous access (401),
duplicate email validation (400), missing profiles (404) and PUT/DELETE (405).
Follow-up reads confirmed rejected changes did not alter stored values.

The run created two fictional local accounts. Runtime credentials are absent
from the collection file. These are own desktop tests, not the official PM
suite. File uploads, media serving, profile lists and the frontend flow remain
unverified. PATCH is therefore not marked fully complete yet.

### Upload checks in the Django test runner

After configuring MEDIA_ROOT, MEDIA_URL and local media routing, executed
`python manage.py test --verbosity 1`: **33 test methods passed**.
Three new multipart tests verify an owner's GIF upload and its saved bytes,
rejection of another user's upload (403) and rejection of an empty file (400).
Temporary upload directories are removed after the tests. These checks do
not prove image-content validation: the model currently uses FileField.
Upload testing in Postman, HTTP media retrieval and frontend verification
remain open.

### Upload checks in the Postman desktop app

The first upload run did not finish: the imported file reference did not
supply a file, so PATCH returned 200 with file=null. The media-URL assertion
failed and the following GET could not be sent. Two fictional accounts were
created by that attempt; no successful upload is claimed for it.

Copied the neutral fixture to the Postman working directory as
coderr-testbild.gif and corrected both multipart requests to use that relative
filename. Imported the corrected collection as
`Coderr Day 6 - Profile Upload Local Files` and ran all six requests with
one iteration, No Environment, Keep variable values disabled and stored
cookies disabled. The run started at 15:44:14 on 4 November 2026.

| Requests | Assertions | Passed | Failed | Skipped | Execution errors |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 6 | 23 | 23 | 0 | 0 | 0 |

The owner upload returned 200 with a media URL. GET of that URL returned 200,
image/gif and GIF89a data. A foreign upload returned 403; a subsequent profile
read confirmed the original file URL was preserved. Duration: 516 ms.
This second run created another two fictional accounts which remain locally.
The source fixture and sanitized collection are in postman/. Runtime
credentials are absent from the repository files. The complete frontend
upload flow and image-content validation remain unverified.

### Profile list endpoints in the Django test runner

Executed `python manage.py test --verbosity 1`: **40 test methods passed**.
Two serializer tests verify the documented field sets. Five list endpoint
tests cover anonymous access (401), both authenticated roles reading both
lists, type filtering, arrays without pagination, empty lists and rejected
write methods (405). A query-count test with two profiles per type observed
two queries per request: token authentication and the joined profile/user
list. This is a query-count check, not a measured before/after comparison.
Both list endpoints still require Postman desktop verification.

### Profile lists in the Postman desktop app

Imported `postman/coderr-day6-lists.postman_collection.json` and ran all ten
requests with one iteration, No Environment, Keep variable values disabled
and stored cookies disabled. Run time: 16:46:14 on 4 November 2026; 574 ms.

| Requests | Assertions | Passed | Failed | Skipped | Execution errors |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 42 | 42 | 0 | 0 | 0 |

Both Customer and Business tokens could read both arrays. Every returned
profile had the expected type and exact documented field set. The newly
registered accounts were included. Anonymous reads returned 401; POST requests
returned 405. Two additional fictional local accounts remain after the run.
No runtime credentials are stored in the collection file. The complete
frontend flow is still open.

### Customer profile in the supplied frontend

Started the separate frontend on 127.0.0.1:5501 and used the backend on
127.0.0.1:8001. In the browser, registered fictional Customer account
alex_kunde_0411, opened its own profile, changed first/last name to Alex Muster
and selected postman/fixtures/testbild.png through the file chooser.
Saved the form, reloaded the page, logged out and logged in again using
the frontend login form. The saved name and blue test image remained visible.
Both profile/header image elements referenced the backend media URL.
An ORM/file read confirmed the stored name and that the PNG bytes match the
fixture. No personal image or real contact address was used.

The frontend only accepts PNG/JPEG previews, so this check used a PNG rather
than the GIF used in Postman. No frontend source change was required.
Missing review/order/offer/base-info endpoints still cause errors on their
respective pages; they belong to later work. The Customer own-profile page
showed a review-loading error. This is a successful targeted profile check,
not a claim that the whole frontend works. The Business edit form and public
profile pages remain unverified.

### Business profile in the supplied frontend

Registered fictional Business account mara_anbieter_0411 in the browser.
Edited its name, phone, location, description and working hours, and uploaded
the PNG fixture through the file chooser. After saving, reloading, logging
out and logging in again through the frontend form, all edited fields and
the blue image remained visible. Both profile/header image elements used
the stored media URL. An ORM/file read confirmed the edited values and PNG
bytes. Django stored a different filename to preserve the existing Customer
upload with the same original name. No frontend source edits were required.

The review-loading error remains visible because that endpoint is scheduled
for later work. Offers, orders, reviews, statistics, public profile pages,
guest logins and the complete platform workflow are not claimed as verified.

### Day 6 final checks

Final `python manage.py test --verbosity 1`: **40 test methods passed**.
`manage.py check` reported no issues; `makemigrations --check --dry-run`
reported no changes; `migrate --check` succeeded; `pip check` found no broken
requirements. Pip disabled its unavailable local cache, without affecting
the dependency check. `git diff --check` passed. Git ignore checks confirmed
that .env, the database, media uploads and local planning files stay excluded.
No model changes or new migration were needed for Day 6.

## Day 7 – 5 November 2026

Added Offer and OfferDetail models and applied offers_app.0001_initial to the
local database. Both new tables were confirmed present and empty. Admin list
and add pages for both models returned 200 using Django's test client with an
existing superuser; this was not a browser or Postman check.

Added fourteen automated offer tests covering numeric/string prices,
unlimited revisions, invalid field values, required fields, numeric JSON price
output, three distinct package types, package counts, nested validation and
optional images. Creation checks verify linked packages, server-supplied
ownership and rollback of the offer and first package when the second package
fails. These tests use a separate test database where needed.

Final `python manage.py test --verbosity 1`: **54 test methods passed**.
System checks reported no issues. `makemigrations --check --dry-run` reported
no changes; `migrate --check` and `git diff --check` succeeded.

No offer endpoint was tested in Postman or the frontend: offer views, routes
and role permissions are still pending. No additional API checklist item is
complete. FileField does not validate image content. Database rollback does
not provide cleanup for uploaded files in external file storage.

## Day 8 – Offer creation, 7 November 2026

Added POST /api/offers/ with token authentication, a business-profile
permission and server-supplied ownership. All 60 automated test methods passed.

Ran postman/coderr-day8-create-offers.postman_collection.json in the Postman
Desktop Runner at 13:11:43: eight requests, 36 assertions passed, zero failed,
skipped or execution errors, duration 642 ms. One iteration, No Environment,
Keep variable values disabled, stored cookies disabled.

The run checked registration of two fictional accounts, business creation
with three packages (201), anonymous access (401), customer access (403),
missing and duplicate package types (400), and zero delivery time (400).
Successful output includes offer/package IDs, numeric prices, expected package
fields and a null image. Two accounts and one offer remain in the local
backend. Runtime credentials were not exported. Offer read/update/delete
routes and frontend verification remain pending.

### Offer and package reads in Postman Desktop

On 7 November 2026 at 14:06:22, ran
postman/coderr-day8-read-offers.postman_collection.json: 11 requests,
53 assertions passed, zero failed/skipped assertions or execution errors,
465 ms. One iteration, No Environment, Keep variable values disabled,
stored cookies disabled. No runtime credentials were exported.

Verified both roles can read offers and packages, exact response fields,
owner IDs, numeric minimum price and independently calculated minimum delivery
time, absolute package links, following the basic package link, anonymous
401 responses and missing-object 404 responses. The run created two additional
fictional accounts and one offer with three packages, retained locally.
The full automated suite previously passed 65 tests after the read endpoints
were added. Updates, deletion and frontend verification remain pending.

### Partial offer updates in Postman Desktop

On 7 November 2026 at 15:22:23, ran
postman/coderr-day8-update-offers.postman_collection.json: 12 requests,
51 assertions passed, zero failures, skips or execution errors; 498 ms.
One iteration, No Environment, Keep variable values disabled, stored cookies
disabled. Two fictional accounts and one updated offer remain locally.

Verified changing only the basic price preserves package IDs, other package
fields and offer fields. Subsequent GET requests confirmed persistence and
that rejected edits did not change the offer. Foreign customer PATCH returned
403; anonymous PATCH 401; missing/repeated package types and zero delivery time
400; an unknown offer returned 404. Staff/foreign-user rejection and transaction
rollback were additionally covered by the previously executed automated suite,
which passed all 72 test methods. No runtime credentials were exported.
Deletion and frontend verification remain pending.

### Offer deletion in Postman Desktop

On 7 November 2026 at 15:57:30, ran
postman/coderr-day8-delete-offers.postman_collection.json: 12 requests,
47 assertions passed, zero failed/skipped assertions or execution errors,
484 ms. One iteration, No Environment, Keep variable values disabled,
stored cookies disabled. No runtime credentials were exported.

Created a disposable offer, verified foreign customer deletion returns 403
and anonymous deletion returns 401, then confirmed the offer and packages
still exist. Owner deletion returned 204 with an empty body. GET for that
offer and each of its three packages returned 404; repeated DELETE also
returned 404. The two new fictional accounts remain locally; the disposable
offer and its packages were removed. The previously executed automated suite
passed all 76 tests, including preservation of unrelated offers and the owner.
Frontend verification and the Day 8 commit remain pending.

### Targeted frontend read check – 8 November 2026

Opened offer.html?id=2 in the supplied frontend on port 5501 while signed in
as the existing fictional Business user mara_anbieter_0411. The test offer's
title, description and provider username rendered. Switched through all three
package tabs: Basic showed 100.5 EUR and 7 days, Standard 200 EUR and 5 days,
Premium 200 EUR and 2 days; unlimited revisions and the Logo feature rendered.
No frontend source change was made.

The page also displayed errors for currently missing supporting endpoints,
including reviews. Order counts and reviews are not verified. Frontend creation,
updates and deletion remain pending. Their list refresh uses GET /api/offers/
with creator filtering and pagination, scheduled for Days 9–10.

### Day 8 final backend checks – 8 November 2026

All 76 automated test methods passed. Django system checks reported no issues;
makemigrations --check --dry-run reported no changes; migrate --check and
git diff --check succeeded. Full frontend CRUD remains deferred until the
planned offer list/filtering/pagination work.

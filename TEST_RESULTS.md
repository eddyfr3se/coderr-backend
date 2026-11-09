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

## Day 9 – List filters, 8 November 2026

Added public offer listing with provider details, initial six-item pagination,
django-filter 26.2, creator/minimum-price/maximum-delivery filters and DRF
search/ordering. Existing dependency versions were preserved. All 97 automated
test methods passed. Tests include independent aggregate filters, combinations,
boundaries, malformed numeric input, title/description search and both ordering
directions. Anonymous list requests used three queries for one and three offers.

Ran postman/coderr-day9-filters.postman_collection.json in Postman Desktop
12.35.5 at 02:50:58: 19 requests, 68 assertions passed, zero failed/skipped
assertions or execution errors; 776 ms. One iteration, No Environment,
Keep variable values disabled, stored cookies disabled.

Verified public creator filtering, provider output, inclusive price/delivery
bounds, case-insensitive title/description search, ascending/descending price
and update-time ordering, combined filters, empty values, no matches and 400
responses for invalid numeric parameters. Two fictional accounts and three
offers remain locally. No runtime credentials were exported. Extended
pagination checks and frontend list/filter workflows remain open.

### Frontend list checks – 9 November 2026

Used the supplied frontend on port 5501 while signed in as the fictional
Business user Mara. Searching Logo returned Logo Starter (50 EUR, seven days)
and Website Express (100 EUR, two days). Applying the three-day delivery limit
retained only Website Express; clearing it restored both. Descending price
ordering placed Website Express first. Searching kein-treffer-0911 displayed
the expected empty-results message, then restoring Logo restored both offers.
No frontend source changes were made. The homepage still reports missing
statistics data; that endpoint is not implemented yet. Extended pagination
and full frontend offer creation/editing/deletion remain pending for Day 10.

### Day 9 final checks – 9 November 2026

All 97 automated tests passed again (0.900 seconds). Django system checks
reported no issues; makemigrations --check --dry-run reported no changes.
migrate --check, pip check and git diff --check succeeded. Local learning
documents, .env and the development database remain excluded from Git.

## Day 10 – Pagination, 9 November 2026

Added eight automated pagination tests for custom page sizes, next/previous
navigation, complete results without duplication, retained filter/search/order
parameters, oversized pages, empty sizes/results and invalid parameters.
The initial run found four failing subcases: page_size abc, 0, -1 and 1.5
returned 200 because DRF silently used the default size. Added explicit positive
integer validation; these values now return 400 with a page_size error.
Missing/empty page_size still uses six. Invalid or nonexistent page numbers
retain DRF's 404 response. No maximum page size has been introduced.

After the change, all 105 automated test methods passed in 0.932 seconds;
Django system checks reported no issues and git diff --check succeeded.
Day 10 pagination checks in Postman Desktop and the frontend are pending.

### Pagination in Postman Desktop – 9 November 2026

Ran postman/coderr-day10-pagination.postman_collection.json in Desktop 12.35.5.
The first run at 11:15:55 had 64 passed and four failed assertions, zero skipped
assertions/execution errors, 678 ms. The four failures were an incorrect test
expectation: page_size errors contain a string, not an array. Status 400 was
already correct. Corrected these assertions without changing backend behavior.

The rerun at 11:17:05 passed all 68 assertions across 21 GET requests, with
zero failed/skipped assertions or execution errors, 421 ms. One iteration,
No Environment, Keep variable values disabled, stored cookies disabled.
Verified page sizes one/two/twenty/empty, next/previous navigation, last-page
remainder, total count, retained filters/search/ordering in links, empty results,
400 for invalid sizes and DRF's 404 for invalid/nonexistent pages.

This collection reads the three retained Day 9 offers for Business ID 24
(offer IDs 5, 6, 7). It creates or deletes no data and needs no authentication.
Its fixture dependency is documented in the collection description. Frontend
pagination and full offer creation/editing/deletion remain pending.

### Frontend creation and pagination – 9 November 2026

The database initially contained six offers, so no second default-size page
existed. Signed in as the existing fictional Business user Mara, created
Website für ein Café through the own-profile form with three packages:
basic 180 EUR/seven days/two revisions, standard 280 EUR/five days/three
revisions, premium 380 EUR/three days/five revisions; each has one feature.
The success message appeared and the offer rendered in the owner's list.
No image was uploaded. Missing supporting review endpoints still produce
profile-page errors and are outside this check.

Opened the unfiltered public offer list: page 1 showed the six existing offers.
Clicked page 2: only the newly created offer appeared, showing 180 EUR and
three days, with page 2 highlighted and the next arrow disabled. Clicking the
previous arrow restored the original six offers on page 1. The new offer
remains locally. No frontend source was changed. Frontend editing/deletion
and their list-refresh behavior remain pending.

### Frontend editing and deletion – 9 November 2026

In Mara's own-profile editor, changed offer 8 to Website für ein Café mit
Speisekarte and changed its Basic price from 180 to 190 EUR. The success
message and owner list reflected both changes; a page reload preserved them.
Read-only database inspection confirmed package IDs 22, 23 and 24 remained
unchanged. Standard/Premium prices remained 280/380 EUR and delivery times
remained seven/five/three days.

Deleted this disposable offer through the frontend editor. The success message
appeared and the owner's list became empty, including after reload. Read-only
database inspection confirmed offer 8 and packages 22/23/24 no longer exist,
while the six original offers (1, 2, 3, 5, 6, 7) remain. The public list then
rendered those six offers with only page 1. No offer image was uploaded and no
frontend source was changed. Supporting reviews/orders/statistics remain open.

Marked all six offer operations complete in the local checklist and the
opened official documentation. The Day 10 milestone covers offer operations,
pagination and the checked frontend flows; no official Academy PM result
or complete platform integration is claimed.

## Day 11 – Order model, 9 November 2026

Added six model tests for initial status/timestamps, user reverse relations,
stored values remaining unchanged after source package edits, preservation of
orders after offer deletion, invalid field/status validation, unlimited
revisions, documented statuses and independent JSON-list defaults.
All 111 automated test methods passed in 0.947 seconds; Django system checks
reported no issues. Applied orders_app.0001_initial successfully.

The tests construct orders directly through a helper; they do not prove API
creation, authenticated ownership assignment or role/visibility enforcement.
Order API endpoints, Postman and frontend order checks remain pending.

### Order serializers – 9 November 2026

Added eight serializer tests. Verified copied package values, server-supplied
customer/provider ownership, read-only input protection, exact response fields,
numeric JSON price, write-only offer_detail_id, required/malformed input,
unknown-package Http404 without order creation, and saved values surviving
source changes/deletion. The serializer receives customer_user through save();
HTTP authentication and role enforcement are not covered by these unit tests.

All 14 orders_app tests passed, then all 119 project test methods passed in
0.944 seconds. Django system checks and git diff --check succeeded.
Order views, routing, Postman Desktop and frontend order flows remain pending.

### Order creation/list API – 9 November 2026

Added 12 API tests using DRF's APIClient with actual token headers. Verified
Customer creation (201), documented fields, server-supplied users/price/status,
Business/profileless-staff rejection (403), anonymous GET/POST (401), missing
or malformed package IDs (400), unknown packages (404), and no creation after
rejected requests. Verified participant-only arrays for customers/providers,
empty arrays for unrelated users including staff, original prices after source
edits, and unsupported collection methods (405). Listing used two queries
(token authentication plus orders) with one and three orders.

All 26 orders_app tests passed, then all 131 project test methods passed in
1.026 seconds. Django system checks and git diff --check succeeded. These
are automated checks; Postman Desktop and frontend order checks remain pending.

### Order creation/list in Postman Desktop – 9 November 2026

Ran postman/coderr-day11-orders.postman_collection.json in Postman Desktop
12.35.5 at 15:50:01: 24 requests, all 83 assertions passed, zero failed/skipped
assertions or execution errors; 799 ms. One iteration, No Environment,
Keep variable values disabled, stored cookies disabled.

Created four fictional accounts (two Customers, two Businesses), an offer with
three packages and two orders. Verified Customer creation (201), package values,
server-assigned users, status/timestamps, participant-only arrays, empty arrays
for unrelated users, Business rejection (403), anonymous requests (401), missing
or malformed IDs (400), unknown package (404), ignored ownership/price/status
input and no orders from rejected requests. After changing the offered Basic
price from 180.50 to 220 EUR, both orders retained 180.50 EUR.

All four accounts, the offer and both orders remain locally. No runtime
credentials were exported. Marked GET/POST /api/orders/ complete in the local
checklist and the opened official documentation. Frontend order creation and
list rendering remain pending; status updates/deletion are planned for Day 12.

### Frontend order creation and participant views – 9 November 2026

Prepared offer 10, Website für einen Blumenladen, directly through the local
ORM for existing fictional Business user Mara (ID 14). It has basic/standard/
premium packages 28/29/30 priced 80/120/160 EUR with delivery times four/three/
two days, two revisions and the Startseite feature. This fixture preparation
was not performed through the frontend.

Signed in through the frontend as existing fictional Customer Alex. Searched
Blumenladen, opened offer 10, checked the Basic confirmation (80 EUR/four days/
two revisions), and submitted through the local order dialog. The success
message appeared. Status check opened the Customer profile showing order 3,
provider Mara, basic Blumenladen, 80 EUR, four days, two revisions and status
In Bearbeitung. Reloading preserved it. Signed in as Mara and confirmed the
same order with buyer Alex and the same package values in the provider view.
No frontend source changes were made. The fixture and order remain locally.
Reviews, statistics and order counters still produce expected missing-endpoint
messages; status-changing controls were not tested because their API is pending.

### Day 11 final checks

The previously executed complete suite passed all 131 test methods. Final
Django system checks reported no issues; makemigrations --check --dry-run
reported no changes; migrate --check and git diff --check succeeded.
Creation/list APIs and their checked frontend flow complete the Day 11 scope.

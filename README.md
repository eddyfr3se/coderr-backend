# Coderr Backend

## Installation

Requirements: Python 3.14 (used locally), pip and Git.
Clone the backend first if you do not already have a local checkout
(repository access is required while it is private):

```bash
git clone https://github.com/eddyfr3se/coderr-backend.git
cd coderr-backend
```

Run these commands from the backend project directory on macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Generate a local Django secret key:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Replace `replace-with-your-local-secret-key` in `.env` with the generated key.
Put the key inside double quotes. Django loads `.env` automatically through
`python-dotenv`; no shell exports are required. Keep this file private.
Do not overwrite an existing configured `.env` when repeating these steps.

Create the database tables:

```bash
python manage.py migrate
```

[Start](#start-the-backend) · [Frontend](#frontend) ·
[Project status](#project-status) · [Checks](#checks) ·
[Development diary](DEVELOPMENT_DIARY.md)

## Start the backend

From the backend directory:

```bash
source .venv/bin/activate
python manage.py runserver 127.0.0.1:8001
```

- API base URL: `http://127.0.0.1:8001/api/`
- Admin login: `http://127.0.0.1:8001/admin/`
- Stop your terminal's server with Control+C.

An admin account is not created automatically. To create one locally, run
`python manage.py createsuperuser` and follow the interactive prompts.
This admin account is separate from normal Customer/Business API accounts.

## Frontend

Use the [provided Academy frontend](https://github.com/Developer-Akademie-Backendkurs/project.Coderr)
in a separate sibling directory named `Coderr_Frontend`.
It is not part of this backend repository.

If it has not been downloaded yet, run from the backend directory:

```bash
git clone https://github.com/Developer-Akademie-Backendkurs/project.Coderr.git ../Coderr_Frontend
```

Prepared frontend version: **1.2.1**, as listed in its changelog.
Source commit: `31d1e195d639e8bce91f87c5b330b9d040ef5c46`.

In the separate frontend's `shared/scripts/config.js`, use:

```javascript
const API_BASE_URL = 'http://127.0.0.1:8001/api/';
const STATIC_BASE_URL = 'http://127.0.0.1:8001/';
```

Those two addresses are the only frontend changes made during setup.
The supplied guest login values have not been changed. Matching demo accounts
have not been created, so guest login is not ready.

Keep Django running. In a second terminal, from the backend directory:

```bash
source .venv/bin/activate
python -m http.server 5501 --bind 127.0.0.1 --directory ../Coderr_Frontend
```

Open `http://127.0.0.1:5501/` in your browser. The backend allows frontend
origins `http://127.0.0.1:5501` and `http://localhost:5501` through CORS.
Registration, login, own-profile loading/editing and PNG upload were checked
in the browser for Customer and Business accounts, including a fresh login.
Offer detail rendering and all three package tabs were also checked. Offer
search, delivery filtering, descending price ordering and empty search results
were checked in the browser. Creating a three-package offer, editing its title
and Basic price, persistence after reload, deletion and navigation between
six-item pages were also checked. Offer-image uploads were not part of this
frontend check.
Order creation and order-list rendering were checked in the browser for a
Customer and the receiving Business. A provider status change to completed
persisted after reload and appeared in the Customer profile with unchanged
package values. Provider counters and review display were checked. A Customer
created a disposable review, changed its text and rating, verified persistence
after reload and deleted it. Platform statistics remain pending.

### Temporary ports

Coderr currently uses backend port **8001** and frontend port **5501** so the
existing KanMind development servers can continue using 8000 and 5500.

When switching Coderr to 8000/5500 later, update these together:

- Backend and frontend start commands.
- Both backend addresses in the frontend's `shared/scripts/config.js`.
- `CORS_ALLOWED_ORIGINS` in `core/settings.py`.
- README instructions and any Postman environment created by then.

## Project status

This project currently contains the Django setup, application skeletons and
the UserProfile model with its initial migration and admin configuration.
The model stores the Customer/Business type, optional profile details, a file
reference and the creation timestamp. Uploaded files are stored locally in
`media/profiles/` and served under `/media/` when DEBUG is enabled. The media
directory is excluded from Git. The current FileField does not validate
image contents; the supplied frontend previews PNG/JPEG files.
Registration and login are available:

- `POST /api/registration/`: username, email, password, repeated_password and
  type (`customer` or `business`); returns HTTP 201.
- `POST /api/login/`: username and password; returns HTTP 200.

Both responses contain token, username, email and user_id. Passwords are
processed with Django's password hashing and never included in responses.
Registration rejects duplicate usernames, duplicate emails regardless of
letter case, mismatched passwords, missing fields and unsupported types.
The email uniqueness check is serializer validation, not a database constraint.
Username uniqueness uses Django's standard user behavior.

Public auth endpoints do not require a token. Profile endpoints require
`Authorization: Token <token>`:

- `GET /api/profile/{pk}/`: read a profile by user ID.
- `PATCH /api/profile/{pk}/`: update only your own profile; accepts JSON for
  text fields or multipart/form-data with `file` for an upload.
- `GET /api/profiles/business/`: array of Business profiles.
- `GET /api/profiles/customer/`: array of Customer profiles.

PATCH returns the complete profile. Account type, username and owner cannot
be changed through this serializer. Customer-list `uploaded_at` currently
uses the profile creation timestamp, not the time of an image replacement.
Offer listing is public; the other offer endpoints require token authentication:

- `GET /api/offers/`: paginated public list with provider details. Supports
  creator_id, min_price, max_delivery_time, search and ordering; the default
  page size is six. Use page and a positive integer page_size for navigation;
  invalid sizes return 400, invalid/nonexistent pages return DRF's 404.
  Missing/empty page_size uses six. Search covers title/description; ordering supports
  min_price and updated_at, with a leading minus for descending order.
- `POST /api/offers/`: Business users create an offer with exactly one basic,
  standard and premium package; returns 201.
- `GET /api/offers/{id}/`: authenticated users read an offer with package links,
  minimum price and minimum delivery time.
- `GET /api/offerdetails/{id}/`: authenticated users read a complete package.
- `PATCH /api/offers/{id}/`: only the owner updates selected fields. Identify
  packages by offer_type; omitted fields and package IDs are preserved.
- `DELETE /api/offers/{id}/`: only the owner deletes an offer and its packages;
  returns 204 with no response body.

Offer creation and nested updates use database transactions. Filesystem writes
are not rolled back by database transactions. Offer images use media/offers/.
The offer list, filters and pagination are implemented and checked.

Order endpoints require token authentication:

- `POST /api/orders/`: Customers create an order from offer_detail_id; returns
  201. The backend assigns the authenticated customer and the package's
  provider. Missing/malformed IDs return 400; unknown packages return 404.
- `GET /api/orders/`: unpaginated array containing only orders involving the
  authenticated user as customer or provider. Staff receive no wider listing.
- `PATCH /api/orders/{id}/`: the assigned Business user changes only status to
  in_progress, completed or cancelled. Missing/invalid status and extra fields
  return 400. Returns the complete updated order.
- `DELETE /api/orders/{id}/`: Staff only; returns 204 with an empty body.

Orders store package values at creation, so later offer changes or deletion
do not change existing orders. Deleting a linked customer/provider account
cascades to its orders. Initial status is in_progress. The PATCH documentation
specifies Business access; this implementation also requires provider ownership
to prevent changes to foreign orders.

- `GET /api/order-count/{business_user_id}/`: count in-progress orders.
- `GET /api/completed-order-count/{business_user_id}/`: count completed orders.

Both counters require authentication and return 404 for unknown or non-Business
users. Business users without matching orders receive zero.

Review endpoints require token authentication:

- `GET /api/reviews/`: unpaginated list; filter by business_user_id or reviewer_id,
  and order by rating or updated_at (prefix with minus for descending order).
- `POST /api/reviews/`: Customers review a Business user with rating 1–5 and
  description. The backend assigns the reviewer; duplicate pairs return 400.
- `PATCH /api/reviews/{id}/`: only the author changes rating and description;
  extra fields return 400. Staff cannot edit another author's review.
- `DELETE /api/reviews/{id}/`: only the author deletes; returns an empty 204.

The Review model enforces rating limits and unique reviewer/provider pairs in
SQLite. Platform statistics at `/api/base-info/` remain pending.

Applications:

- `auth_app`: registration, login and profiles.
- `offers_app`: offers and packages.
- `orders_app`: orders and order counters.
- `reviews_app`: reviews and platform statistics.

The project uses SQLite locally. The database, environment secrets, virtual
environment and local planning files are excluded from Git.
This setup is for local development with `DJANGO_DEBUG=True`.

## Checks

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --check
python -m pip check
```

Checks and their actual results are recorded in
[TEST_RESULTS.md](TEST_RESULTS.md). No official Academy PM result is claimed.

### Automated tests

```bash
python manage.py test
```

The first three tests in `core/tests.py` check admin routing and access:
the login page is public, anonymous visitors are redirected to login,
and an active staff user can open the admin index. Django creates a separate
test database; the development server does not need to be running.
The staff test uses a session login helper, not the future API token login.

Six model tests in `auth_app/tests.py` additionally check both valid profile
types, invalid-type validation, optional defaults, duplicate-profile validation
and deletion behavior in both directions. These are model tests, not API
or Postman checks. A plain model save does not automatically call full_clean.

Twelve API tests additionally exercise registration and login, including role
profiles, hashed passwords, token creation/reuse, invalid credentials, inactive
users, required fields, duplicates and unsupported GET methods.
Nineteen tests in `auth_app/test_profiles.py` cover profile serializers,
partial updates, email validation, permissions, uploads, filtered lists,
unsupported methods and query counts. Upload tests use temporary directories
that are cleaned up.

Fourteen tests in `offers_app/tests.py` cover package and offer validation,
nested creation, server-supplied ownership and database rollback when package
creation fails. Twenty-two additional offer API/update/delete tests cover
permissions, output fields, package links, partial updates, rollback and deletion
cascades. Twenty-one list tests cover filters, search, ordering, public access,
output fields, basic pagination and query counts. These areas account for
97 automated test methods.

Eight additional tests in `offers_app/test_pagination.py` cover page sizes,
navigation, retained query parameters, empty results and invalid parameters.
Forty tests in orders_app cover model validation, stored package values,
serializers, creation permissions, participant visibility and query counts.
They also cover status validation, object permissions, protected fields,
staff-only deletion and preservation of related records.
Four counter tests, three review model tests and ten review API tests cover
counts, rating limits, duplicate prevention, filters and author permissions.
The current total is **162 automated test methods**.

### Postman desktop tests

Import [the authentication collection](postman/coderr-day5-auth.postman_collection.json)
into the Postman desktop app. Use **No Environment** to avoid overriding its
`base_url`, which is `http://127.0.0.1:8001/api`.

Run all 18 requests in order with one iteration. Disable **Keep variable
values** and enable **Run collection without using stored cookies**.
The first request generates unique fictional usernames, example emails and a
random local test password. Responses supply tokens for the login comparison.
Each run creates two local test accounts; no account deletion API is available
yet, so the accounts remain in the local database.

The desktop Runner run on 2 November 2026 passed all **82 assertions** with
zero failures, skipped assertions or execution errors. This is a local test
collection, not the official Academy PM suite. Do not export runtime passwords
or tokens into repository files.

Day 6 adds these desktop collections. Run each collection in order with the
same settings as above; each creates two fictional local accounts.

| Collection | Requests | Passed assertions, 4 November 2026 |
| --- | ---: | ---: |
| [Profiles](postman/coderr-day6-profiles.postman_collection.json) | 15 | 51 |
| [Uploads](postman/coderr-day6-upload.postman_collection.json) | 6 | 23 |
| [Profile lists](postman/coderr-day6-lists.postman_collection.json) | 10 | 42 |

Before running the upload collection, copy `postman/fixtures/testbild.gif`
to your Postman working directory as `coderr-testbild.gif`, or select that
fixture in both multipart upload requests. These runs had no failed/skipped
assertions or execution errors. An earlier unsuccessful upload run and its
file-reference correction are documented in [TEST_RESULTS.md](TEST_RESULTS.md).

### Offer collections

Import the four `postman/coderr-day8-*-offers.postman_collection.json` files
into Postman Desktop. Run each collection in order with one iteration and
No Environment. Disable Keep variable values and enable Run collection without
using stored cookies. Each collection creates two fictional local accounts;
create/read/update runs retain their test offer, while the delete run removes
only its newly created disposable offer and packages. Do not export runtime
credentials. Recorded results: create 36, read 53, update 51 and delete 47
passed assertions; see TEST_RESULTS.md for dates and scope.

The Day 9 collection, `postman/coderr-day9-filters.postman_collection.json`,
uses the same Runner settings and creates two fictional accounts and three
offers which remain locally. Its 19 requests passed all 68 assertions in
Postman Desktop on 8 November 2026. It checks public listing, numeric filters,
search, ordering, combinations, empty results and malformed parameters.

The read-only Day 10 collection,
`postman/coderr-day10-pagination.postman_collection.json`, requires the retained
Day 9 fixtures: three offers belonging to Business ID 24 (adjust business_id
if using an equivalent fixture elsewhere). It creates no accounts or offers.
Run with the same Runner settings. All 68 assertions across 21 requests passed
in Postman Desktop on 9 November 2026 after correcting four test expectations;
see TEST_RESULTS.md for the initial failure and rerun.

### Order collection

Import `postman/coderr-day11-orders.postman_collection.json` and use the same
Runner settings. It creates four fictional accounts, an offer with three
packages and two orders; all remain locally. It checks order creation, input
and permission errors, participant-only lists, protected server values and
unchanged order prices after an offer-price change. The Desktop run on
9 November 2026 passed all 83 assertions across 24 requests. Runtime passwords
and tokens must not be exported.

The Day 12 collection, `postman/coderr-day12-orders.postman_collection.json`,
uses the same Runner settings. Supply a token from a dedicated local Staff
test account temporarily as staff_token before running; clear the variable
and revoke the token afterwards. The collection contains no saved credentials.
Its 34 requests passed all 111 assertions in Postman Desktop on 10 November
2026. It creates four fictional API accounts, an offer and two orders, deletes
only its new disposable order, and retains the control order and offer.
Status changes, role/ownership rejection, forbidden fields, empty 204 deletion
and preservation of the control data are checked.


### Day 13 counters and reviews

Use the same Desktop Runner settings for these collections. The runs on
11 November 2026 passed without failures:

| Collection | Requests | Passed assertions |
| --- | ---: | ---: |
| `coderr-day13-counts.postman_collection.json` | 11 | 18 |
| `coderr-day13-reviews.postman_collection.json` | 9 | 15 |
| `coderr-day13-review-edits.postman_collection.json` | 11 | 22 |

These local collections use existing Business fixtures, including Mara (ID 14)
and the second counter provider (ID 26). Inspect the request expectations before
using a different database. They create fictional Customer accounts which remain
locally. The creation collection retains its review; the edit/delete collection
removes only its own disposable review. Runtime credential variables are empty
in the repository files. See TEST_RESULTS.md for the Desktop reimport and browser
checks.

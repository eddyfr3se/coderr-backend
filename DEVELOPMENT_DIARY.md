# Development diary

## Day 2 – Project setup, 22 October 2026

- Created a local Python 3.14.7 virtual environment.
- Installed Django 5.2.18, Django REST Framework 3.18.3,
  django-cors-headers 4.9.0 and python-dotenv 1.2.4.
- Recorded installed packages and dependencies in requirements.txt.
- Created the core project and four empty application skeletons:
  auth_app, offers_app, orders_app and reviews_app, each with an api directory.
- Configured automatic .env loading and a private local secret key.
- Configured local hosts, SQLite, token authentication and authenticated access
  by default. Individual public endpoints will be added explicitly later.
- Applied Django's standard database migrations. No custom business models
  or demo users have been created.
- Initialized local Git and reviewed the 60 backend files before committing.
- Saved the initial setup as commit 83cac18, "Set up Coderr Django backend".
- Created the private repository https://github.com/eddyfr3se/coderr-backend,
  configured origin and pushed main successfully. The separate frontend,
  local planning files, database and private environment were not uploaded.
- Downloaded the Academy frontend into a separate sibling directory.
  Frontend version: 1.2.1; source commit:
  31d1e195d639e8bce91f87c5b330b9d040ef5c46.
- Changed only API_BASE_URL and STATIC_BASE_URL to backend port 8001.
  Configured the backend to allow frontend port 5501 through CORS.
- Kept KanMind running on 8000/5500. Started Coderr on 8001/5501.
- Added installation and start instructions to the README.

API features, guest login, business permissions and frontend workflows still
need implementation and testing. New concepts will be explained as they arise.

## Day 3 – Routing and first automated tests, 23 October 2026

- Reviewed central URL routing and the empty app-level API URL files.
- Added three admin access checks in core/tests.py using APITestCase,
  setUp, named URLs with reverse, DRF status constants and assertions.
- Demonstrated an incorrect expectation: loading the admin login page returned
  200 while the test deliberately expected 201. The first run had one failure
  and two successful tests. Corrected the expectation and ran all tests again.
  This was an assertion exercise, not a new feature implemented with TDD.
- All three tests passed in the final run. Django used an in-memory test
  database. A before/after SHA-256 comparison confirmed that the development
  database file was unchanged during that run.
- The staff test uses force_login to prepare a session. It does not test
  passwords, the API login endpoint or token authentication.
- Existing local formatting changes in core/settings.py were left unchanged.
- Repeated the test command manually in the Antigravity terminal. The result
  was three successful tests in 0.019 seconds; the terminal output was checked.

No business endpoints or extra production routes were added. Token tests and
business validation tests will follow when those endpoints are implemented.

## Day 4 – Profile model and admin, 29 October 2026

- Added UserProfile linked to the configured Django user through OneToOneField.
- Added customer/business choices, optional location, telephone, description,
  working hours, a FileField and an automatic creation timestamp.
- Kept names and email on Django's standard user model. File validation and
  media serving remain part of the later upload implementation.
- Generated and applied auth_app.0001_initial. Registered profiles in admin
  with search, type filters and related-user loading.
- Created the local admin account and checked the signed-in admin interface.
  Restarted only Coderr on port 8001 to load the new model/admin code.
- Created a fictional profile fixture through admin for profiltest_customer,
  a separate local user with no usable password. Verified the stored values.
- Added six model checks using the existing APITestCase tooling. Checked
  roles, validation, empty defaults, timestamps, uniqueness validation and
  deletion behavior. All nine current tests passed.
- Confirmed there are no pending migrations or unrecorded model changes.

No API endpoint is complete or marked as done. Postman checks begin with
registration/login. The local fixtures remain in the ignored database.
The previously existing settings.py formatting change remains separate.

## Day 5 – Registration and login, 2 November 2026

- Compared the official auth request/response contracts with the KanMind
  serializers and adapted the approach for username-based registration/login.
- Added serializer validation, password confirmation, email duplicate checks
  and user/profile creation inside a Django database transaction.
- Added public APIViews and named routes for registration and login.
  Return only token, username, email and user_id. Login uses authenticate;
  passwords are hashed through create_user rather than saved as plain text.
- Added twelve API tests. Together with the existing tests, all 21 passed.
- Imported a new, separate 18-request Coderr collection into the Postman
  desktop app. Left KanMind collections unchanged and selected No Environment
  so their base URL could not override Coderr's port 8001.
- Ran the collection locally: 82 assertions passed, no failed/skipped
  assertions or execution errors. Keep variable values was disabled and
  stored cookies were not used. Verified the two created accounts have
  the appropriate profiles and tokens and no staff/superuser privileges.
- Marked registration and login in the browser endpoint checklist and local
  requirement list. All other operations remain open.

The full frontend registration/login workflow has not yet been checked in the
browser. Profile loading is still unimplemented. Token authentication against
a protected business endpoint will be tested once that endpoint exists.

## Day 6 – In progress, 4 November 2026

- Added separate serializers for profile output and partial updates.
- Added an owner permission and a RetrieveUpdateAPIView with a named route.
  Profile lookup uses the user ID. Related user data is loaded together.
- Verified 30 automated test methods and ran the new 15-request collection
  in the Postman desktop app: all 51 assertions passed with no errors.
- Reading and text updates work with token authentication. File uploads,
  media configuration, profile lists and frontend verification remain open.

- Configured MEDIA_ROOT/MEDIA_URL and development-only media routing.
- Added three upload tests; all 33 automated test methods passed.
- Corrected a missing local file reference in Postman. The repeated upload
  run passed all 23 assertions, including media retrieval and owner checks.
  The unsuccessful first attempt is recorded in TEST_RESULTS.md.
- Profile lists and the complete frontend flow remain open for Day 6.

- Added separate Business/Customer list serializers and read-only list
  endpoints with token authentication. Querysets filter by profile type and
  load related users together. Lists return arrays without pagination.
- All 40 automated test methods passed. List checks include access control,
  type filtering, empty lists, unsupported methods and query counts.
  Postman checks for these lists and the complete frontend flow remain open.

- Ran all ten profile-list requests in the Postman desktop app: all 42
  assertions passed, no errors. Marked both list operations complete in the
  local endpoint checklist. Frontend verification remains open.

- Started the supplied frontend separately on port 5501. Verified Customer
  registration, login, own-profile loading, name editing and PNG upload in
  the browser, including persistence after reload and a fresh login.
- Confirmed saved PNG bytes match the test fixture. No frontend source
  changes were needed. Business profile editing remains to be checked;
  missing later endpoints still cause visible errors elsewhere on the page.

- Verified Business registration/login, profile editing and PNG upload in
  the supplied frontend, including persistence after a fresh login. Confirmed
  stored fields and uploaded bytes. No frontend source changes were needed.
- Completed the Day 6 profile scope. Errors from the later review/offer/order
  and statistics endpoints remain outside this milestone. Updated the README
  with profile routes, upload storage and current test instructions.

## Day 7 – 5 November 2026

- Added Offer and OfferDetail models, linked by ForeignKey, and applied their
  initial migration. Registered both models in the admin with search,
  package-type filtering and related-object loading.
- Added explicit package and offer serializers. Validation requires exactly
  one basic, standard and premium package. Prices use decimal values; delivery
  time starts at one day and revisions allow -1 for unlimited revisions.
- Added nested creation inside a database transaction. The caller supplies
  the owner; API authentication and business-role checks follow with the view.
- All 54 automated tests passed, including fourteen offer tests. Migration
  consistency and admin page responses were checked. No offer Postman or
  frontend checks were run because those API routes are not implemented yet.

## Day 8 – In progress, 7 November 2026

- Added the offer creation route, CreateAPIView and business-user permission.
  The view assigns the authenticated user as owner.
- Added six API tests; the full suite passed all 60 test methods.
- Ran eight requests in Postman Desktop: all 36 assertions passed. Creation,
  anonymous/customer rejection and invalid packages were verified.
- Offer retrieval, package retrieval, updates, deletion and frontend checks
  remain open. Day 8 has not been committed or pushed yet.

- Added authenticated offer/package retrieval with separate output serializers.
  Offer queries calculate independent price/delivery minima and prefetch packages.
- All 65 automated tests passed after implementing the read endpoints.
- Verified reads in Postman Desktop: 11 requests, all 53 assertions passed.
  Marked both read operations complete in the local requirements checklist.
  Offer updates, deletion and frontend checks remain open.

- Added owner-only PATCH with package selection by offer_type, stable IDs,
  preservation of omitted fields and transactional updates. All 72 automated
  test methods passed, including rollback and foreign staff rejection.
- Ran the partial-update collection in Postman Desktop: 12 requests and all
  51 assertions passed. Marked PATCH complete in the local checklist.
  Deletion and frontend verification remain open; Day 8 is not yet committed.

- Enabled owner-only DELETE through RetrieveUpdateDestroyAPIView. All 76
  automated tests passed, including package cascade and unrelated data checks.
- Postman Desktop deletion run: 12 requests, all 47 assertions passed. The
  disposable offer and all three packages returned 404 after owner deletion.
  Marked DELETE complete locally. Frontend checks and final commit remain open.

- On 8 November, checked offer detail rendering in the supplied frontend and
  switched all three package tabs. Titles, prices, delivery times and unlimited
  revisions rendered correctly. Supporting review/order endpoints remain open.
- The frontend's creation/update/delete dialogs refresh the offer list; that
  list still requires the filtering/pagination work planned for Days 9–10.
  No complete frontend CRUD workflow is claimed yet.

- Completed the Day 8 backend checks on 8 November: all 76 tests passed and
  migrations are consistent. Updated README routes and Postman instructions.
  Full frontend CRUD remains scheduled after offer list/filtering/pagination.

## Day 9 – 8–9 November 2026

- Added public GET /api/offers/ while preserving business-only POST. Added
  provider output and initial six-item pagination to match the frontend.
- Installed django-filter 26.2 and added creator, minimum-price and maximum
  delivery filters. Added DRF title/description search and price/date ordering.
- All 97 automated tests passed. Postman Desktop filter run passed all 68
  assertions across 19 requests.
- On 9 November, checked the supplied frontend: Logo search returned the two
  matching offers, a three-day delivery limit retained Website Express, and
  clearing the limit restored both. Descending price ordering put 100 EUR
  before 50 EUR. An unmatched search showed the empty-results message.
- Updated README status and test documentation. Detailed pagination and full
  frontend offer creation/editing/deletion remain scheduled for Day 10.

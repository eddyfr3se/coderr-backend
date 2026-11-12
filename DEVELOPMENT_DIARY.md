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

## Day 10 – 9 November 2026

- Reviewed the official offer-list requirements and DRF pagination behavior.
  Added eight pagination tests; the first run exposed silent fallback for four
  invalid page_size values. Added positive integer validation returning 400.
- All 105 automated tests now pass. Navigation preserves filters/search/order
  and page size; invalid page numbers retain DRF's 404 response. Postman Desktop,
  frontend pagination and full frontend offer workflows remain pending.
- Ran the pagination collection in Postman Desktop against retained Day 9
  fixtures. The first run found four incorrect error-shape assertions; corrected
  string expectations and reran. All 68 assertions across 21 requests passed.
  No test data was created or deleted. Frontend checks remain pending.
- Created Website für ein Café with three packages through Mara's own-profile
  form, bringing the local total from six offers to seven. The public frontend
  displayed six on page 1 and only the new offer on page 2; the previous arrow
  restored page 1. No frontend code changed. Editing/deletion remain pending.
- Edited the Café title and Basic price in the frontend, then reloaded to
  confirm persistence. Package IDs and the other package values were retained.
  Deleted the disposable offer through the frontend; its three packages were
  removed, the original six offers remained, and the second public page
  disappeared. No offer image was uploaded.
- Marked all six offer operations complete locally and in the official
  documentation. Updated README and the test report for the Day 10 milestone.

## Day 11 – 9 November 2026

- Added Order with separate customer/business user relations, stored package
  values, documented status choices and timestamps. Registered it in admin.
  Package values are independent of subsequent offer changes/deletion; deleting
  either linked user cascades to their orders, as configured on both relations.
- Created and applied orders_app.0001_initial. Six model tests passed alongside
  existing tests: 111 automated test methods passed. API creation, customer-role
  enforcement and participant-only listing are not implemented or tested yet.
- Added read-only order output and creation serializers. The input requires
  offer_detail_id; creation copies package values and derives the provider from
  its offer. The future view must pass the authenticated customer to save().
- Eight new serializer tests passed, including output shape, numeric prices,
  ignored read-only input, missing/malformed/unknown package IDs and stored
  values surviving package changes/deletion. All 119 tests passed. No order
  HTTP endpoint or Postman check is implemented at this stage.
- Connected GET/POST /api/orders/ through ListCreateAPIView. POST requires an
  authenticated Customer; the view supplies the requesting user to save(). GET
  returns an unpaginated array filtered to customer/provider participation.
- Twelve API tests passed, covering creation, input tampering, role/auth errors,
  invalid/missing packages, visibility, preserved prices, unsupported methods
  and constant query counts. All 131 project tests passed. Postman verification
  is pending; neither order operation has been marked complete yet.
- Postman Desktop run passed all 83 assertions across 24 requests. Checked
  Customer creation, role/auth/input errors, visibility, ignored ownership/price
  overrides and original order prices after an offer-price change. Four new
  fictional accounts, one offer and two orders remain locally. Marked GET/POST
  orders complete locally and in the official documentation. Frontend checks
  and the Day 11 commit remain pending.
- Prepared a local three-package offer for Mara through the ORM, then used
  Alex's frontend account to place its Basic order for 80 EUR. Confirmed order
  3 after reload in the Customer profile and in Mara's provider profile.
  No frontend code changes were needed. The fixture and order remain locally.
- Completed final Django/migration/whitespace checks and updated the README.
  Day 11 covers creation and participant lists; status updates and staff
  deletion remain scheduled for Day 12.

## Day 12 – 10 November 2026

- Added PATCH/DELETE /api/orders/{id}/. PATCH requires both a Business profile
  and assignment as the order's provider; DELETE requires is_staff. The
  documentation specifies Business for PATCH without explicitly describing
  foreign providers. Applied the narrower ownership rule to prevent foreign
  order changes; no mentor confirmation of that interpretation is claimed.
- Added a status-only serializer: required documented status, full output and
  400 for extra fields. Added 14 API tests; all 145 project tests passed.
  Postman Desktop, frontend status changes and the Day 12 commit are pending.
- Postman Desktop passed all 111 assertions across 34 requests. Verified role
  and object permissions, status/field validation, unchanged agreement values,
  staff-only empty-204 deletion and preservation of the control order/offer.
- Supplied a temporary local staff token as a collection variable because
  CSV iteration data required a paid plan. Cleared/revoked the token afterwards,
  disabled the staff fixture and removed the temporary data file. No credentials
  were exported to the repository. Marked PATCH/DELETE complete locally and in
  the official documentation. Frontend status checks remain pending.
- In the supplied frontend, Mara changed existing local order 3 from
  in_progress to completed. Reloading preserved it. Alex's Customer profile
  showed the same completed order with unchanged 80 EUR price, four days,
  two revisions and Startseite feature. Read-only before/after comparison
  confirmed only status and updated_at changed. No frontend code was changed.
- Completed final Django/migration/whitespace checks and updated the README
  and test report. The Day 12 scope is complete; counters follow on Day 13.

## Day 13 – Order counts and reviews

- Added authenticated counts for in-progress and completed orders. Both routes
  reuse one view, check that the target is a Business user, and count matching
  orders in the database. Four new automated tests passed; total: 149.
  Postman Desktop, frontend verification and reviews remain open.
- Verified both counters with Postman CLI (18 assertions across 11 requests);
  the Desktop Runner's Start run control was disabled. Confirmed Mara's
  completed count (1) and queue count (0) in the frontend.
- Checked off both counter routes in the browser and local requirements list.
  Added and migrated the Review model, registered it in Django admin, and
  added database constraints for ratings 1–5 and one review per customer/provider
  pair. Review API endpoints remain open.
- Implemented authenticated review listing with provider/reviewer filters and
  rating/update-time ordering. Customers can create reviews for Business users;
  the server assigns the reviewer. Duplicate creation returns 400, one of the
  two statuses listed in the course documentation for that case.
- Ran 15 passing Postman CLI assertions across 9 review requests. Confirmed
  the four-star test review appears on Mara's provider profile and checked off
  GET/POST reviews in both checklists.
- Repeated both Day 13 collections in Postman Desktop: 15 review assertions
  and 18 counter assertions passed. Reimporting the count collection under a
  fresh name allowed the run to start.
- Added author-only review PATCH and DELETE, following the Permissions entry
  rather than allowing Staff to edit another author's review. Only rating and
  description are writable. All 162 automated tests and 22 Postman Desktop
  assertions passed. Checked off both routes in the browser and local list.
- Verified the review lifecycle in the supplied frontend as Alex: created a
  disposable four-star review for Mara, changed its text and rating to five,
  and confirmed persistence after reloading. Deleted that same test review
  and confirmed its absence after reloading. No frontend code changes were
  needed. README updates and the Day 13 commit/push remain pending.

- Completed the browser check and updated the README. Django system checks,
  migration consistency checks, dependency checks and whitespace checks passed.


## Day 14 – Separate DRF exercises

- Prepared an isolated local exercise server on port 8002 using the installed
  Django/DRF dependencies, without database models. Excluded learning_local
  from Git. The Coderr API routes and throttling policy remain unchanged.
- Practised a custom rate class, method selection with get_throttles and
  ScopedRateThrottle. Verified independent scope counters in Postman Desktop.
- Compared PageNumberPagination and LimitOffsetPagination with six fixed
  records. Corresponding parameters returned identical record IDs.
- Four Desktop runs passed 39 assertions across 24 requests in total.
  These are separate exercise runs, not a full Coderr regression.
- Compared APIView, generic views and ViewSets conceptually. Existing review
  filtering and ordering were explained; no additional review code was needed.
- Repeated the scoped collection (6/6 assertions) and confirmed a later
  request was allowed after the throttle window (1/1 assertion). The exact
  time boundary was not tested. Recorded results and completed the technical
  exercise work for Day 14.

## Day 15 – Platform statistics

- Added the public base-info route, an explicit output serializer and aggregate
  review statistics. Business profile and offer counts use separate queries;
  the empty rating average returns zero. No new model or migration needed.
- Four new tests and the full 166-test suite passed. Postman Desktop and
  frontend verification remain open.
- Postman Desktop passed all 12 statistics assertions across 5 requests,
  including an anonymous GET compared with local database counts and rejected
  write methods. Frontend verification remains pending.
- Confirmed all four statistics on the frontend home page: 9 offers,
  2 reviews, 15 providers and average 4. Marked base-info complete locally
  and in the browser checklist. Day 15 documentation and final contract
  review remain pending.
- On 13 November, checked all 23 planned routes and HTTP methods, updated
  the README and completed system/migration checks. Statistics implementation
  and its Django, Postman Desktop and frontend checks are complete. Final
  project-wide acceptance remains scheduled for the remaining days.

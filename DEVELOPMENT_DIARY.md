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

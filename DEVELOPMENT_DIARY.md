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

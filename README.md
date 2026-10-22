# Coderr Backend

## Installation

Requirements: Python 3.14 (used locally), pip and Git.
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
This admin account is separate from the future Customer/Business API accounts.

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
The frontend can display its pages, but its API features are not implemented yet.

### Temporary ports

Coderr currently uses backend port **8001** and frontend port **5501** so the
existing KanMind development servers can continue using 8000 and 5500.

When switching Coderr to 8000/5500 later, update these together:

- Backend and frontend start commands.
- Both backend addresses in the frontend's `shared/scripts/config.js`.
- `CORS_ALLOWED_ORIGINS` in `core/settings.py`.
- README instructions and any Postman environment created by then.

## Project status

This project currently contains the Django setup and empty application
skeletons. Registration, login, profiles, offers, orders, reviews and statistics
are not implemented. The `/api/` routes do not expose these features yet.

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

Setup checks and their actual results are recorded in
[TEST_RESULTS.md](TEST_RESULTS.md). No API regression suite has been executed
for Coderr, and no official Academy PM result is claimed.

# College TravelMap

A real-time social map and travel hub for college. Students can create travel plans, add trips, find co-travelers, and coordinate meetups through a live map.

## Tech Stack

- Python 3.12+
- Django 5.2.x (ORM, auth, admin, views)
- django-crispy-forms + crispy-bootstrap5 (form rendering with Bootstrap 5)
- django-dynamic-breadcrumbs (navigation UX)
- Pillow (image handling for carousel/features)
- SQLite (default DB for local dev via Django)
- Leaflet + Leaflet Routing Machine (front-end mapping and routing)
- Requests (server-side HTTP calls for geocoding proxy)

## Quickstart (Clone, Environment, Install, Run Locally)

These commands are for Windows PowerShell. Bash/macOS equivalents are noted where helpful.

1) Clone the repository

```
git clone https://github.com/Lakshya717/TravelMap.git
cd TravelMap
```

2) Create and activate a virtual environment (Python 3.12+ recommended)

PowerShell:

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Bash/macOS:

```
python3 -m venv .venv
source .venv/bin/activate
```

3) Install dependencies

```
pip install -r requirements.txt
```

4) Set up the database and a superuser

```
python manage.py migrate
python manage.py createsuperuser
```

5) Run the development server

```
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser. Admin is at `http://127.0.0.1:8000/admin/`.

Notes:

- Static files are served from `static/` in development; media uploads are stored under `Media/`.
- Default database is SQLite (`db.sqlite3`). No extra setup needed for local development.
- Timezone is set to Asia/Kolkata in `TravelMap/settings.py`.

### Admin access (superuser)

- Create an admin user: `python manage.py createsuperuser`
  - Provide username, email (optional), and password when prompted.
- Log in at: `http://127.0.0.1:8000/admin/`
- Forgot the password? Change it with: `python manage.py changepassword <username>`
- Dev reset (SQLite only): delete `db.sqlite3` and run `python manage.py migrate` again to start fresh.

## What Is This Project?

TravelMap is a dynamic, social mapping application built for college students. Every semester, many students travel long distances between home and campus. TravelMap simplifies coordination: students can create and share travel plans, find groups or co-travelers, share rides between cities, and see trips visualized on a live map.

Instead of scattered group chats, students can create, share, and join plans directly on the map, making it easy to form groups, share rides, and meet up.

## Features

- Live social map (Leaflet + Leaflet Routing Machine)

  - Visualizes all trips with markers and routes.
  - Flights/trains draw smooth great-circle–style arcs; buses/roads use OSRM routing via LRM.
  - Departure-time shading with a gradient or time-bucket controls (hours/days/weeks/months).
  - Route caching: client saves computed routes to the backend (`Trip.route` JSON) to avoid re-querying the routing engine.
- Travel plans and nested trips

  - `Accounts.TravelPlan` with many `Accounts.Trip` items (origin/destination, times, mode, notes, passengers).
  - Create/edit flow uses Django inline formset (`TripFormSet`) for nested trip editing.
  - Pagination for public and personal plan lists.
- Simple plan chat

  - Each plan has a chat thread (`Accounts.ChatMessage`).
  - Fetch-based UI with periodic refresh every 5s; CSRF-protected POST endpoint.
- Authentication and UX

  - User registration (`SignUpForm`), login, logout using Django auth.
  - Redirects configured (`LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL`).
  - Crispy Forms with Bootstrap 5 for consistent styling.
- CMS-like homepage content

  - `UI.carousel`, `UI.features`, and `UI.step` models drive the landing page (carousel, features, and timeline).
  - A context processor (`UI.context_processors.site_settings`) injects these objects globally.
  - `href` values are reversed into internal URLs when possible.
- Geocoding helper API

  - `/geocode/` view calls Nominatim (OpenStreetMap) for location search suggestions (server-side proxy with UA header and basic error handling).
- Sensible defaults for local dev

  - SQLite database, local media (`MEDIA_URL=/Media/`), Bootstrap assets in `static/`, and Leaflet/Leaflet Routing Machine vendored under `static/`.

## Project Structure Overview

```
TravelMap/
├─ manage.py
├─ TravelMap/                # Django project (settings, urls, wsgi/asgi)
├─ Accounts/                 # TravelPlan, Trip, ChatMessage models
├─ UI/                       # Forms, views, urls, context processors, CMS models
├─ templates/                # Django templates (UI/, partials/)
├─ static/                   # Bootstrap, Leaflet, LRM assets
├─ Media/                    # Uploaded images (carousel/features)
├─ requirements.txt
└─ db.sqlite3                # Local dev database
```

## Key URLs

- `/` — Landing page (carousel, features, steps)
- `/map/` — Live social map
- `/travelplans/` — Public plans (paginated)
- `/travelplans/me/` — Your plans
- `/travelplans/me/new/` — Create a new plan + trips
- `/travelplans/<id>/` — Plan detail + chat
- `/api/travelplans/<id>/chat/` — Chat messages API (GET/POST)
- `/api/trips/<id>/route` — Cache a computed route for a trip (POST)
- `/geocode/` — Nominatim search proxy (GET)
- `/admin/` — Django admin

## Environment and Configuration

- `DEBUG=True` by default for development.
- `ALLOWED_HOSTS=[]` (use `python manage.py runserver` locally).
- Change timezone, static, and media settings in `TravelMap/settings.py` if needed.
- Secret key in settings is for local dev only; provide a secure key via environment for production.

## Development Tips

- Log in to `/admin/` and add `carousel`, `features`, and `step` entries to light up the landing page.
- Create a few `TravelPlan` and `Trip` items, then open `/map/` to see routes. For road trips, the first load uses OSRM; subsequent loads use cached geometry when available.
- Geocoding helper at `/search_map/` and `/geocode/` can assist in picking locations.

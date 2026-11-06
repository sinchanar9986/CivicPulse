# CivicPulse – Implementation Plan
## AI-Powered Smart Citizen Complaint Intelligence System

---

## Top-Level Overview

**Goal:** Build a fully functional, locally-hosted web application where citizens submit complaints and administrators manage them through an AI-assisted dashboard.

**Scope:**
- Citizen-facing complaint submission form with image upload and location input
- AI classification (TF-IDF keyword model) into 6 categories: Road Damage, Garbage, Drainage, Water Leakage, Streetlight, Other
- Duplicate complaint detection using TF-IDF + cosine similarity
- Automatic priority assignment (High / Medium / Low) based on category + keyword severity
- Admin dashboard with status management, filters, statistics charts, and an interactive Leaflet.js map
- SQLite database with full schema; no paid APIs or external services required

**Out of scope for v1:**
- User authentication for citizens (complaints are anonymous)
- Email/SMS notifications
- Multi-language support

**Technology Stack:**
- Backend: Python 3.10+, Flask, SQLAlchemy (ORM), Flask-WTF (forms)
- AI/NLP: scikit-learn (TF-IDF, cosine similarity), NLTK (tokenization/stopwords)
- Database: SQLite (file-based, zero-config)
- Frontend: HTML5, CSS3 (custom + Bootstrap 5), JavaScript (vanilla + Chart.js + Leaflet.js)
- Image upload: Werkzeug (bundled with Flask)

---

## Project Folder Structure

```
CivicPulse/
├── app/
│   ├── __init__.py          # Flask app factory, extensions init
│   ├── models.py            # SQLAlchemy models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── citizen.py       # Complaint submission routes
│   │   └── admin.py         # Admin dashboard routes
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── classifier.py    # TF-IDF category classifier
│   │   ├── duplicate.py     # Cosine similarity duplicate detection
│   │   └── priority.py      # Priority scoring logic
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   ├── map.js       # Leaflet map logic
│   │   │   └── charts.js    # Chart.js dashboard charts
│   │   └── uploads/         # Saved complaint images (gitignored)
│   └── templates/
│       ├── base.html         # Shared layout
│       ├── citizen/
│       │   ├── index.html    # Landing / submission form
│       │   ├── success.html  # Submission confirmation
│       │   └── track.html    # Citizen status tracker
│       └── admin/
│           ├── dashboard.html
│           ├── complaints.html
│           ├── complaint_detail.html
│           └── map.html
├── instance/
│   └── civicpulse.db        # SQLite database (auto-created)
├── config.py                # App configuration constants
├── run.py                   # Entry point
├── init_db.py               # One-time database initializer
├── requirements.txt
└── README.md
```

---

## Database Design

### Table: `complaints`

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| title | VARCHAR(200) | Required |
| description | TEXT | Required |
| category | VARCHAR(50) | AI-assigned or user-selected |
| location_text | VARCHAR(300) | Human-readable address/landmark |
| latitude | FLOAT | Optional, for map pin |
| longitude | FLOAT | Optional, for map pin |
| priority | VARCHAR(10) | High / Medium / Low |
| status | VARCHAR(20) | Pending / In Progress / Resolved |
| image_filename | VARCHAR(255) | Null if no image uploaded |
| is_duplicate | BOOLEAN | Flag set by duplicate detector |
| duplicate_of_id | INTEGER FK | Points to original complaint id |
| similarity_score | FLOAT | Cosine similarity score (0–1) |
| submitted_at | DATETIME | Auto-set on insert |
| updated_at | DATETIME | Auto-updated on change |

### Table: `admin_notes`

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| complaint_id | INTEGER FK | References complaints.id |
| note | TEXT | Admin comment |
| created_at | DATETIME | Auto-set on insert |

---

## Development Phases

### Phase 1 — Project Scaffold & Configuration
### Phase 2 — Database Models
### Phase 3 — AI Engine (Classifier, Duplicate Detector, Priority)
### Phase 4 — Citizen-Facing Routes & Templates
### Phase 5 — Admin Dashboard Routes & Templates
### Phase 6 — Map Integration (Leaflet.js)
### Phase 7 — Charts & Statistics
### Phase 8 — Polish, Validation & README

---

## Sub-Tasks

---

### Sub-Task 1 — Project Scaffold & Configuration
**Status:** `[x] done`

**Confirmed Design Decisions (from user approval):**
- Admin auth: session-based with password read from `ADMIN_PASSWORD` environment variable; stored as a bcrypt hash in `config.py`
- Map default center: Bengaluru, Karnataka (lat: 12.9716, lng: 77.5946)
- Categories: Garbage, Road Damage, Drainage, Water Leakage, Streetlight, Other (6 total)
- Seed data: realistic sample complaints covering all 6 categories
- Image upload: optional, jpg/jpeg/png/gif, max 5 MB, server + client validated

**Intent:**
Establish the complete folder structure, Flask app factory, configuration file, entry point, and `requirements.txt` so every subsequent sub-task has a working skeleton to build on.

**Expected Outcomes:**
- All directories and `__init__.py` files exist
- `flask run` starts without errors (returns a 404, which is expected at this stage)
- `requirements.txt` lists all dependencies with pinned versions
- `config.py` defines `SECRET_KEY`, `SQLALCHEMY_DATABASE_URI`, `UPLOAD_FOLDER`, `MAX_CONTENT_LENGTH`, `ALLOWED_EXTENSIONS`, and `ADMIN_PASSWORD` (read from environment variable `CIVICPULSE_ADMIN_PASSWORD`, default hashed with bcrypt)

**Todo List:**
1. Create all directories as shown in the folder structure above
2. Write `config.py` with `DevelopmentConfig` class
3. Write `app/__init__.py` as a Flask app factory that loads config, initializes SQLAlchemy, and registers blueprints
4. Write `run.py` to call the factory and start the dev server
5. Write `requirements.txt` listing: Flask, Flask-SQLAlchemy, Flask-WTF, scikit-learn, nltk, Werkzeug, WTForms, bcrypt (for password hashing)

**Relevant Context:**
- Flask app factory pattern: `create_app(config)` in `app/__init__.py`
- Blueprints: `citizen_bp` (prefix `/`) and `admin_bp` (prefix `/admin`)
- SQLAlchemy instance created in `app/__init__.py`, imported by `models.py`

---

### Sub-Task 2 — Database Models & Initialization
**Status:** `[ ] pending`

**Intent:**
Define the SQLAlchemy ORM models and provide a one-command database initializer so the SQLite file and all tables are created before the app first runs.

**Expected Outcomes:**
- `app/models.py` defines `Complaint` and `AdminNote` models with all columns from the DB design above
- `python init_db.py` creates `instance/civicpulse.db` with correct schema
- Model relationships: `AdminNote.complaint` → `Complaint`, `Complaint.admin_notes` backref

**Todo List:**
1. Write `app/models.py` with `Complaint` model (all columns above, with `__repr__` for debugging)
2. Write `AdminNote` model with FK to `Complaint`
3. Add `@staticmethod` helper on `Complaint` to list valid statuses and categories
4. Write `init_db.py` that calls `db.create_all()` inside app context and seeds 3–5 sample complaints for testing
5. Verify `python init_db.py` runs without errors

**Relevant Context:**
- SQLAlchemy `db` instance lives in `app/__init__.py`
- `instance/` folder is Flask's default instance path; SQLite URI: `sqlite:///civicpulse.db`
- `updated_at` uses `onupdate=datetime.utcnow` on the column definition

---

### Sub-Task 3 — AI Engine
**Status:** `[ ] pending`

**Intent:**
Implement the three AI modules — category classifier, duplicate detector, and priority scorer — as standalone Python modules so they can be unit-tested independently of Flask.

**Expected Outcomes:**
- `app/ai/classifier.py`: `classify(title, description) → str` — returns one of the 6 category labels (Garbage, Road Damage, Drainage, Water Leakage, Streetlight, Other) using a keyword-weighted TF-IDF approach (no training data file needed; rules are embedded)
- `app/ai/duplicate.py`: `find_duplicate(title, description, existing_complaints) → (bool, int|None, float)` — returns `(is_dup, original_id, score)` using TF-IDF vectorization + cosine similarity with a configurable threshold (default 0.75)
- `app/ai/priority.py`: `assign_priority(category, description) → str` — returns High / Medium / Low based on category default + urgency keyword boosting (keywords like "accident", "flooding", "no water" → High)

**Todo List:**
1. Write `app/ai/classifier.py` with a `CATEGORY_KEYWORDS` dict mapping each category to weighted keyword lists; implement `classify()` using keyword scoring, fallback to "Other" if no category scores above threshold
2. Write `app/ai/duplicate.py` using `sklearn.feature_extraction.text.TfidfVectorizer` + `sklearn.metrics.pairwise.cosine_similarity`; combine title + description as the document for vectorization
3. Write `app/ai/priority.py` with a `CATEGORY_DEFAULT_PRIORITY` dict and `URGENCY_KEYWORDS` list; implement `assign_priority()` with keyword scan override
4. Write simple smoke-test assertions at the bottom of each file (under `if __name__ == "__main__":`) to verify correctness without a test framework

**Relevant Context:**
- NLTK is listed as a dependency for stopword removal inside the TF-IDF vectorizer (pass `stop_words="english"` to `TfidfVectorizer` — no separate NLTK download needed for this)
- The classifier does NOT require a trained model file; it is a deterministic keyword-scoring function
- Duplicate check runs against all non-resolved complaints retrieved from the DB before insertion

---

### Sub-Task 4 — Citizen-Facing Routes & Templates
**Status:** `[ ] pending`

**Intent:**
Build the public-facing pages: the complaint submission form, a submission-success confirmation, and a complaint status tracker where citizens can look up their complaint by ID.

**Expected Outcomes:**
- `GET /` renders the submission form with fields: title, description, category (dropdown with AI suggestion note), location text, latitude, longitude (hidden, populated by map click), image upload
- `POST /submit` validates input, runs classifier + duplicate detector + priority scorer, saves to DB, redirects to `/success/<id>`
- `GET /track` renders a search form; `POST /track` looks up complaint by ID and displays its current status, category, priority, and any admin notes
- Form validation: title (5–200 chars), description (20–2000 chars), category required, location required
- Image upload: max 5 MB, allowed extensions: jpg, jpeg, png, gif; saved to `app/static/uploads/` with a UUID filename

**Todo List:**
1. Write `app/routes/citizen.py` with `citizen_bp` blueprint; implement `index`, `submit`, `success`, and `track` view functions
2. Write `app/templates/base.html` with Bootstrap 5 CDN, navbar, flash message block, and footer
3. Write `app/templates/citizen/index.html` with the complaint form; include a small embedded Leaflet map for location picking (lat/lng auto-fill hidden inputs on marker drop)
4. Write `app/templates/citizen/success.html` showing complaint ID, category detected, priority, duplicate warning if flagged
5. Write `app/templates/citizen/track.html` with search form and conditionally rendered complaint card
6. Add `WTForms` form class `ComplaintForm` in `app/routes/citizen.py` with all validators

**Relevant Context:**
- Image saved using `werkzeug.utils.secure_filename` + `uuid.uuid4()` prefix
- On duplicate detection, complaint is still saved but `is_duplicate=True` and `duplicate_of_id` are set; citizen sees a polite notice
- Flash messages used for form errors

---

### Sub-Task 5 — Admin Dashboard Routes & Templates
**Status:** `[ ] pending`

**Intent:**
Build the administrator interface: a summary dashboard, a filterable complaint list, a complaint detail/edit page, and status update functionality.

**Expected Outcomes:**
- `GET /admin/` shows summary stats: total complaints, counts by status, counts by category, counts by priority
- `GET /admin/complaints` shows paginated table (20/page) with filter controls: status, category, priority, date range, search keyword; duplicate complaints are visually flagged
- `GET /admin/complaints/<id>` shows full complaint detail with image preview, AI scores, admin notes history; includes status update dropdown + note textarea + submit button
- `POST /admin/complaints/<id>/update` updates status and appends an admin note; redirects back to detail page
- `GET /admin/complaints/<id>/delete` soft-deletes (marks status as "Archived") — no hard deletes
- Admin section has a session-based password gate; password is read from `CIVICPULSE_ADMIN_PASSWORD` env var (bcrypt-hashed); no user table needed

**Todo List:**
1. Write `app/routes/admin.py` with `admin_bp` blueprint; implement `dashboard`, `complaints_list`, `complaint_detail`, `update_complaint`, and `delete_complaint` view functions
2. Implement a `@login_required` decorator for admin routes using Flask session; add `/admin/login` and `/admin/logout` routes
3. Write `app/templates/admin/dashboard.html` with stat cards (total, pending, in-progress, resolved) and placeholder chart canvases
4. Write `app/templates/admin/complaints.html` with filter form, sortable table, pagination controls, and duplicate badge
5. Write `app/templates/admin/complaint_detail.html` with full complaint info, image preview, status form, notes timeline
6. In `config.py`, read `ADMIN_PASSWORD_HASH` from environment variable `CIVICPULSE_ADMIN_PASSWORD`; use `bcrypt.checkpw()` for verification at login; document the env var in README

**Relevant Context:**
- Flask session stores `admin_logged_in = True` after login
- Pagination uses SQLAlchemy `.paginate(page, per_page=20)`
- Status choices: Pending, In Progress, Resolved, Archived

---

### Sub-Task 6 — Leaflet.js Map Integration
**Status:** `[ ] pending`

**Intent:**
Add an interactive map to the admin dashboard showing all geo-tagged complaints as color-coded markers, and add a location-picker mini-map to the citizen submission form.

**Expected Outcomes:**
- `GET /admin/map` renders a full-page Leaflet map with OpenStreetMap tiles; markers colored by status (red=Pending, orange=In Progress, green=Resolved)
- Clicking a marker opens a popup with: complaint title, category, location text, status, and a link to the detail page
- Complaints without lat/lng coordinates are excluded from the map but listed in a sidebar
- Citizen submission form has a small embedded map; clicking the map drops a pin and auto-fills the hidden latitude/longitude inputs and the location text field via reverse geocoding (Nominatim, free, no key needed)
- Map gracefully degrades: if tiles fail to load, a static text fallback is shown

**Todo List:**
1. Write `app/static/js/map.js` with two modes: `initAdminMap(complaints)` and `initPickerMap(inputIds)`
2. Define marker icon colors using Leaflet `divIcon` with inline CSS (no external icon files needed)
3. Write `app/templates/admin/map.html` extending base; embed Leaflet CSS/JS from CDN; pass complaint data as a JSON array via `json_filter` or `tojson` Jinja filter
4. Add a `/admin/map/data` API endpoint in `admin.py` that returns JSON of all geo-tagged complaints
5. Update `app/templates/citizen/index.html` to call `initPickerMap()` on the location section
6. Use Nominatim reverse geocoding (`https://nominatim.openstreetmap.org/reverse`) as a fetch call from JS to populate location text on pin drop

**Relevant Context:**
- Leaflet.js CDN: `https://unpkg.com/leaflet@1.9.4/dist/leaflet.js`
- Nominatim usage policy: max 1 request/second; citizen form only calls it on pin drop (user-triggered), so rate limit is not a concern
- Map center defaults to Bengaluru, Karnataka (lat: 12.9716, lng: 77.5946) — configurable in `config.py` as `MAP_DEFAULT_LAT` and `MAP_DEFAULT_LNG`

---

### Sub-Task 7 — Charts & Statistics
**Status:** `[ ] pending`

**Intent:**
Implement the visual analytics section of the admin dashboard using Chart.js, pulling live data from the database.

**Expected Outcomes:**
- Admin dashboard shows 4 charts:
  1. **Doughnut chart** — complaints by status (Pending / In Progress / Resolved)
  2. **Bar chart** — complaints by category
  3. **Line chart** — complaints submitted per day (last 30 days)
  4. **Bar chart (horizontal)** — complaints by priority
- All chart data is fetched from a `/admin/stats` JSON endpoint (no page reload needed)
- Charts are responsive and resize with the browser window

**Todo List:**
1. Add `/admin/stats` route in `admin.py` that queries the DB and returns JSON with keys: `by_status`, `by_category`, `by_priority`, `by_date`
2. Write `app/static/js/charts.js` with `initDashboardCharts(statsUrl)` that fetches the stats endpoint and renders all 4 Chart.js charts
3. Add Chart.js CDN script tag to `base.html` (loaded only on admin pages via a `{% block scripts %}` extension)
4. Update `app/templates/admin/dashboard.html` to include 4 `<canvas>` elements with appropriate IDs and call `initDashboardCharts('/admin/stats')`

**Relevant Context:**
- Chart.js CDN: `https://cdn.jsdelivr.net/npm/chart.js`
- Colors: use a consistent palette defined in `charts.js` (Bootstrap 5 semantic colors)
- The `/admin/stats` endpoint does NOT require authentication so that charts can reload without session issues (data is not sensitive aggregates)

---

### Sub-Task 8 — Styling, Validation, Error Handling & README
**Status:** `[ ] pending`

**Intent:**
Apply the final professional UI polish, add server-side and client-side input validation, implement Flask error pages, and write the complete README with setup and run instructions.

**Expected Outcomes:**
- `app/static/css/style.css` defines a clean civic-themed color scheme (primary: `#1a5276` navy blue; accent: `#2ecc71` green; background: `#f4f6f7`)
- All form inputs have server-side validation (WTForms) and client-side `required`/`minlength`/`maxlength` HTML5 attributes
- Custom 404 and 500 error pages styled consistently with the app
- File upload validated on both client (JS) and server (extension + size check)
- `README.md` includes: project description, feature list, tech stack, prerequisites, step-by-step install + run instructions, default admin credentials, folder structure overview, and screenshot placeholders
- Application tested end-to-end: submit a complaint, verify classification, check duplicate detection, update status from admin, view on map and charts

**Todo List:**
1. Write `app/static/css/style.css` with: color variables, navbar style, card components, form styles, badge colors for priority/status, responsive grid overrides, map container sizing
2. Register `404` and `500` error handlers in `app/__init__.py`; write corresponding templates `app/templates/404.html` and `app/templates/500.html`
3. Add client-side JS validation in `index.html` for file type/size check before form submit
4. Add `MAX_CONTENT_LENGTH = 5 * 1024 * 1024` to config and handle `RequestEntityTooLarge` exception
5. Write `README.md` with full setup instructions (pip install, init_db, flask run, admin login)
6. Do a final end-to-end check: submit complaint → view in admin → update status → view on map → view charts

**Relevant Context:**
- Admin password is set via `CIVICPULSE_ADMIN_PASSWORD` environment variable; default dev password `admin123` documented in README with a clear warning to change before any production use; bcrypt hash generated at app start if env var is set
- The `instance/` folder and `app/static/uploads/` should be added to `.gitignore`

---

## Testing Strategy

Since this is a local v1 build, testing is done through manual smoke-tests and inline assertion checks:

| What | How |
|---|---|
| AI modules (classifier, duplicate, priority) | `if __name__ == "__main__":` assertions in each file; run with `python app/ai/classifier.py` etc. |
| DB schema | `python init_db.py` must complete without errors |
| Form validation | Submit empty/invalid forms; verify errors are shown |
| Image upload | Upload an oversized file; verify rejection message |
| Duplicate detection | Submit the same complaint twice; verify duplicate flag on second |
| Admin login gate | Access `/admin/` without logging in; verify redirect to `/admin/login` |
| Map rendering | Open `/admin/map`; verify markers appear for seeded data |
| Charts | Open `/admin/`; verify all 4 charts render with seeded data |

---

## Dependency List (requirements.txt)

```
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.1
WTForms==3.1.2
scikit-learn==1.4.2
nltk==3.8.1
Werkzeug==3.0.3
bcrypt==4.1.3
```

> **Note:** No paid APIs. No cloud services. Runs entirely on `localhost`.

---

## Setup & Run (Summary)

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize the database (creates instance/civicpulse.db + seeds sample data)
python init_db.py

# 4. Run the application
python run.py

# 5. Open browser
# Citizen form:   http://127.0.0.1:5000/
# Admin login:    http://127.0.0.1:5000/admin/login
# Admin password: set via CIVICPULSE_ADMIN_PASSWORD env var (default: admin123 for dev)
# Windows:  set CIVICPULSE_ADMIN_PASSWORD=admin123
# Mac/Linux: export CIVICPULSE_ADMIN_PASSWORD=admin123
```

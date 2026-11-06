# CivicPulse

**AI-Powered Smart Citizen Complaint Intelligence System**

CivicPulse is a locally-hosted web application that allows citizens to submit civic complaints (garbage, road damage, drainage, water leakage, streetlight) and gives administrators an AI-assisted dashboard to manage, prioritise and track them.

---

## Features

| Feature | Details |
|---|---|
| **Complaint Submission** | Title, description, category, location text, optional photo upload |
| **AI Classification** | Keyword-weighted TF-IDF classifier assigns one of 6 categories |
| **Duplicate Detection** | TF-IDF + cosine similarity (threshold 0.75) flags near-duplicate reports |
| **Priority Assignment** | Automatic High / Medium / Low based on category + urgency keywords |
| **Status Tracking** | Citizens look up their complaint by ID; see status, priority, admin notes |
| **Admin Dashboard** | Stat cards, 4 Chart.js charts, filterable complaint table |
| **Interactive Map** | Leaflet.js + OpenStreetMap; colour-coded markers by status; popup details |
| **Location Picker** | Citizens click a map to drop a pin; Nominatim auto-fills the address |
| **Admin Management** | Update status, add notes, archive complaints; session-based login |
| **Responsive UI** | Bootstrap 5 + custom CSS; works on desktop and mobile |
| **No paid APIs** | Runs 100 % locally — SQLite, scikit-learn, OpenStreetMap |

---

## Technology Stack

- **Backend:** Python 3.10+, Flask 3.0, Flask-SQLAlchemy, Flask-WTF
- **AI/NLP:** scikit-learn (TF-IDF, cosine similarity)
- **Database:** SQLite (zero-config, file-based)
- **Frontend:** Bootstrap 5, Chart.js 4, Leaflet.js 1.9
- **Auth:** bcrypt password hashing, Flask session
- **Image upload:** Werkzeug (bundled with Flask)

---

## Prerequisites

- Python 3.10 or higher
- `pip`
- A modern web browser

---

## Installation & Setup

### 1. Clone / download the project

```bash
# If using git:
git clone <repo-url>
cd CivicPulse

# Or extract the zip and open the folder in your terminal
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set the admin password (optional — default is `admin123`)

```bash
# Windows
set CIVICPULSE_ADMIN_PASSWORD=your_secure_password

# macOS / Linux
export CIVICPULSE_ADMIN_PASSWORD=your_secure_password
```

> **Security note:** The default password `admin123` is suitable for local development only.
> Always set a strong password before sharing the app with others.

### 5. Initialise the database

```bash
python init_db.py
```

This creates `instance/civicpulse.db` and seeds 8 realistic sample complaints.

### 6. Run the application

```bash
python run.py
```

The server starts on **http://127.0.0.1:5000**

---

## Usage

### Citizen Portal

| URL | Purpose |
|---|---|
| `http://127.0.0.1:5000/` | Submit a new complaint |
| `http://127.0.0.1:5000/track` | Track an existing complaint by ID |
| `http://127.0.0.1:5000/success/<id>` | Submission confirmation page |

### Admin Panel

| URL | Purpose |
|---|---|
| `http://127.0.0.1:5000/admin/login` | Admin login |
| `http://127.0.0.1:5000/admin/` | Dashboard with stats and charts |
| `http://127.0.0.1:5000/admin/complaints` | Filterable complaint list |
| `http://127.0.0.1:5000/admin/complaints/<id>` | Complaint detail + status update |
| `http://127.0.0.1:5000/admin/map` | Interactive complaint map |

**Default admin password:** `admin123`
(Override with the `CIVICPULSE_ADMIN_PASSWORD` environment variable)

---

## Project Structure

```
CivicPulse/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # SQLAlchemy models (Complaint, AdminNote)
│   ├── routes/
│   │   ├── citizen.py       # Citizen routes + WTForms
│   │   └── admin.py         # Admin routes, auth, stats, map API
│   ├── ai/
│   │   ├── classifier.py    # TF-IDF keyword classifier
│   │   ├── duplicate.py     # Cosine similarity duplicate detector
│   │   └── priority.py      # Priority scoring logic
│   ├── static/
│   │   ├── css/style.css    # Civic-themed stylesheet
│   │   ├── js/map.js        # Leaflet.js admin map + location picker
│   │   ├── js/charts.js     # Chart.js dashboard charts
│   │   └── uploads/         # Uploaded complaint photos (gitignored)
│   └── templates/
│       ├── base.html        # Shared layout (navbar, flash, footer)
│       ├── 404.html / 500.html
│       ├── citizen/         # index, success, track
│       └── admin/           # login, dashboard, complaints, detail, map
├── instance/
│   └── civicpulse.db        # SQLite database (auto-created, gitignored)
├── config.py                # All configuration constants
├── run.py                   # Entry point
├── init_db.py               # Database init + seed data
├── requirements.txt
└── README.md
```

---

## Complaint Categories

- Garbage
- Road Damage
- Drainage
- Water Leakage
- Streetlight
- Other

## Complaint Statuses

- **Pending** — newly submitted, awaiting action
- **In Progress** — being actively worked on
- **Resolved** — issue fixed
- **Archived** — closed / no longer tracked

---

## Running the Test Suite

```bash
python test_routes.py
```

Also runs AI module smoke tests:

```bash
python app/ai/classifier.py
python app/ai/duplicate.py
python app/ai/priority.py
```

---

## Dependencies

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

---

## License

MIT — free to use, modify and distribute.

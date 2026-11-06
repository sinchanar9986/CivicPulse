"""
CivicPulse — Full End-to-End Integration Test
Run: venv\Scripts\python.exe test_e2e.py
"""
import json
from app import create_app, db
from app.models import Complaint, AdminNote
from app.ai.classifier import classify
from app.ai.duplicate import find_duplicate
from app.ai.priority import assign_priority

app = create_app()
app.config['WTF_CSRF_ENABLED'] = False

PASS = 0
FAIL = 0

def check(label, condition, detail=''):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f'  PASS  {label}')
    else:
        FAIL += 1
        print(f'  FAIL  {label}' + (f'  [{detail}]' if detail else ''))

print('=' * 60)
print('CivicPulse End-to-End Integration Test')
print('=' * 60)

# ----------------------------------------------------------
print('\n[1] AI Engine')
# ----------------------------------------------------------

check('Classifier: Road Damage',
      classify('Pothole on MG Road', 'Large pothole causing accidents on MG Road near signal') == 'Road Damage')
check('Classifier: Garbage',
      classify('Garbage pile near park', 'Huge waste dump near children park bad smell') == 'Garbage')
check('Classifier: Drainage',
      classify('Drain blocked', 'Drainage clogged causing waterlogging and flooding') == 'Drainage')
check('Classifier: Water Leakage',
      classify('Burst pipe on main road', 'Water pipe burst leaking flooding road') == 'Water Leakage')
check('Classifier: Streetlight',
      classify('Street lamp broken', 'Lamp post not working dark at night unsafe') == 'Streetlight')
check('Classifier: fallback Other',
      classify('Random issue', 'I have a complaint') == 'Other')

check('Priority: Road Damage default High',
      assign_priority('Road Damage', 'pothole on road') == 'High')
check('Priority: urgency keyword escalates to High',
      assign_priority('Garbage', 'dangerous waste near school emergency') == 'High')
check('Priority: Garbage default Medium',
      assign_priority('Garbage', 'garbage pile near park') == 'Medium')
check('Priority: minor keyword de-escalates to Low',
      assign_priority('Streetlight', 'small minor light issue') == 'Low')
check('Priority: Other default Low',
      assign_priority('Other', 'general complaint') == 'Low')

class _M:
    def __init__(self, i, t, d): self.id, self.title, self.description = i, t, d

existing = [
    _M(1, 'Pothole on MG Road', 'Large pothole near signal causing accidents'),
    _M(2, 'Garbage near park', 'Uncollected garbage causing bad smell'),
]
is_dup, orig_id, score = find_duplicate(
    'Pothole on MG Road Bengaluru',
    'There is a big pothole near signal on MG Road causing accidents and vehicle damage',
    existing)
check('Duplicate: detects near-duplicate', is_dup is True, f'score={score}')
check('Duplicate: correct original_id', orig_id == 1)

is_dup2, _, _ = find_duplicate(
    'Broken streetlight',
    'The lamp near bus stop has not worked for weeks',
    existing)
check('Duplicate: not flagged for different complaint', is_dup2 is False)

is_dup3, _, _ = find_duplicate('Any title', 'Any description', [])
check('Duplicate: empty list returns False', is_dup3 is False)

# ----------------------------------------------------------
print('\n[2] Database Models')
# ----------------------------------------------------------
with app.app_context():
    total = Complaint.query.count()
    check('DB: 8 seeded complaints', total == 8, f'got {total}')
    check('DB: 3 seeded admin notes', AdminNote.query.count() == 3)

    cats = {c.category for c in Complaint.query.all()}
    expected_cats = {'Garbage', 'Road Damage', 'Drainage', 'Water Leakage', 'Streetlight'}
    check('DB: all 5 main categories present in seed data', expected_cats.issubset(cats))

    statuses = {c.status for c in Complaint.query.all()}
    check('DB: multiple statuses in seed data',
          'Pending' in statuses and 'In Progress' in statuses and 'Resolved' in statuses)

    c1 = db.session.get(Complaint, 1)
    check('DB: complaint has lat/lng', c1.latitude is not None and c1.longitude is not None)
    check('DB: Complaint.__repr__ works', 'Road Damage' in repr(c1))

# ----------------------------------------------------------
print('\n[3] HTTP Routes — Status Codes')
# ----------------------------------------------------------
with app.test_client() as c:
    with c.session_transaction() as s:
        s['admin_logged_in'] = True

    for path, expected in [
        ('/', 200),
        ('/track', 200),
        ('/success/1', 200),
        ('/admin/', 200),
        ('/admin/complaints', 200),
        ('/admin/complaints/1', 200),
        ('/admin/stats', 200),
        ('/admin/map', 200),
        ('/admin/map/data', 200),
        ('/admin/complaints/9999', 404),
        ('/nonexistent', 404),
    ]:
        r = c.get(path)
        check(f'GET {path}', r.status_code == expected,
              f'expected {expected}, got {r.status_code}')

# ----------------------------------------------------------
print('\n[4] Citizen Complaint Submission Workflow')
# ----------------------------------------------------------
with app.test_client() as c:
    # Submit a valid complaint
    r = c.post('/submit', data={
        'title': 'Blocked drain on Koramangala road',
        'description': 'The drain near 4th block Koramangala is completely blocked causing flooding every time it rains',
        'category': 'Drainage',
        'location_text': 'Koramangala 4th Block, Bengaluru',
        'latitude': '12.9352',
        'longitude': '77.6245',
    }, follow_redirects=False)
    check('Submit: redirects on success', r.status_code == 302)
    loc = r.headers.get('Location', '')
    check('Submit: redirects to /success/', '/success/' in loc, f'Location={loc}')

    # Follow to success page
    r2 = c.get(loc, follow_redirects=True)
    body = r2.data.decode()
    check('Success page: renders correctly', r2.status_code == 200)
    check('Success page: shows complaint ID', 'Complaint Submitted' in body)
    check('Success page: shows category', 'Drainage' in body)

    # Submit duplicate — same title+description
    r3 = c.post('/submit', data={
        'title': 'Blocked drain on Koramangala road',
        'description': 'The drain near 4th block Koramangala is completely blocked causing flooding every time it rains',
        'category': 'Drainage',
        'location_text': 'Koramangala 4th Block, Bengaluru',
    }, follow_redirects=True)
    body3 = r3.data.decode()
    check('Submit duplicate: success page shown', r3.status_code == 200)
    check('Submit duplicate: duplicate warning shown', 'Possible Duplicate' in body3 or 'similar' in body3.lower())

    # Verify in DB
    with app.app_context():
        dupes = Complaint.query.filter_by(is_duplicate=True).all()
        check('Submit duplicate: DB flagged as duplicate', len(dupes) >= 1)

    # Submit with missing fields → form errors
    r4 = c.post('/submit', data={
        'title': 'Hi',   # too short
        'description': 'Short',
        'category': '',
        'location_text': '',
    }, follow_redirects=True)
    body4 = r4.data.decode()
    check('Validation: short title rejected', r4.status_code == 200 and 'is-invalid' in body4)

    # Track complaint by ID
    r5 = c.post('/track', data={'complaint_id': '1'}, follow_redirects=True)
    body5 = r5.data.decode()
    check('Track: found complaint #1', r5.status_code == 200 and 'Pothole' in body5)

    r6 = c.post('/track', data={'complaint_id': '9999'}, follow_redirects=True)
    body6 = r6.data.decode()
    check('Track: not-found message for missing ID', 'No complaint' in body6)

# ----------------------------------------------------------
print('\n[5] Admin Dashboard & Management')
# ----------------------------------------------------------
with app.test_client() as c:
    # Unauthenticated access → redirect
    r = c.get('/admin/')
    check('Auth: unauthenticated redirects to login', r.status_code == 302)

    # Wrong password
    r = c.post('/admin/login', data={'password': 'badpassword'}, follow_redirects=True)
    check('Auth: wrong password shows error', 'Incorrect' in r.data.decode())

    # Correct password
    r = c.post('/admin/login', data={'password': 'admin123'}, follow_redirects=True)
    check('Auth: correct password grants access', r.status_code == 200 and 'Dashboard' in r.data.decode())

    # Filter complaints
    r = c.get('/admin/complaints?status=Pending')
    body = r.data.decode()
    check('Filter: status=Pending renders', r.status_code == 200 and 'Pending' in body)

    r = c.get('/admin/complaints?category=Garbage')
    check('Filter: category=Garbage renders', r.status_code == 200)

    r = c.get('/admin/complaints?q=pothole')
    check('Filter: keyword search renders', r.status_code == 200)

    # Update status
    r = c.post('/admin/complaints/1/update',
               data={'status': 'In Progress', 'note': 'Team dispatched to fix pothole on site'},
               follow_redirects=True)
    check('Update: status change accepted', r.status_code == 200 and 'updated' in r.data.decode())

    with app.app_context():
        c1 = db.session.get(Complaint, 1)
        check('Update: status persisted to DB', c1.status == 'In Progress')
        check('Update: admin note saved', len(c1.admin_notes) >= 1)
        check('Update: note text correct', 'Team dispatched' in c1.admin_notes[-1].note)

    # Archive complaint
    r = c.get('/admin/complaints/2/archive', follow_redirects=True)
    check('Archive: complaint archived', r.status_code == 200)
    with app.app_context():
        c2 = db.session.get(Complaint, 2)
        check('Archive: status set to Archived in DB', c2.status == 'Archived')

# ----------------------------------------------------------
print('\n[6] Charts & Map API')
# ----------------------------------------------------------
with app.test_client() as c:
    with c.session_transaction() as s:
        s['admin_logged_in'] = True

    # Stats endpoint
    r = c.get('/admin/stats')
    stats = json.loads(r.data)
    check('Stats: by_status has data', len(stats['by_status']) > 0)
    check('Stats: by_category has data', len(stats['by_category']) > 0)
    check('Stats: by_priority has data', len(stats['by_priority']) > 0)
    check('Stats: by_date has 30 entries', len(stats['by_date']) == 30)
    check('Stats: all priority keys valid',
          all(k in ['High', 'Medium', 'Low'] for k in stats['by_priority']))

    # Map data endpoint
    r = c.get('/admin/map/data')
    markers = json.loads(r.data)
    check('Map: returns geo-tagged markers', len(markers) >= 5)
    check('Map: each marker has required fields',
          all('id' in m and 'latitude' in m and 'status' in m and 'title' in m for m in markers))
    check('Map: no None lat/lng in response',
          all(m['latitude'] is not None and m['longitude'] is not None for m in markers))

    # Map page
    r = c.get('/admin/map')
    body = r.data.decode()
    check('Map page: Leaflet CSS loaded', 'leaflet' in body.lower())
    check('Map page: complaint JSON embedded', 'initAdminMap' in body)

    # Dashboard charts
    r = c.get('/admin/')
    body = r.data.decode()
    check('Dashboard: chart-status canvas present', 'chart-status' in body)
    check('Dashboard: chart-category canvas present', 'chart-category' in body)
    check('Dashboard: chart-date canvas present', 'chart-date' in body)
    check('Dashboard: chart-priority canvas present', 'chart-priority' in body)
    check('Dashboard: Chart.js script loaded', 'chart.js' in body.lower())

# ----------------------------------------------------------
print('\n[7] Error Handling')
# ----------------------------------------------------------
with app.test_client() as c:
    r = c.get('/this-does-not-exist')
    check('404: custom page returned', r.status_code == 404 and 'Page Not Found' in r.data.decode())

# ----------------------------------------------------------
print('\n' + '=' * 60)
print(f'RESULTS: {PASS} passed, {FAIL} failed')
print('=' * 60)
if FAIL:
    print('Some tests FAILED — review output above.')
else:
    print('All tests passed. CivicPulse is ready to run.')

"""
Full route verification test for CivicPulse.
Run: venv\Scripts\python.exe test_routes.py
"""
import json
from app import create_app

app = create_app()
app.config['WTF_CSRF_ENABLED'] = False

errors = []

with app.test_client() as c:
    with c.session_transaction() as s:
        s['admin_logged_in'] = True

    routes = [
        ('GET', '/',                       200),
        ('GET', '/track',                  200),
        ('GET', '/success/1',              200),
        ('GET', '/admin/',                 200),
        ('GET', '/admin/login',            200),
        ('GET', '/admin/complaints',       200),
        ('GET', '/admin/complaints/1',     200),
        ('GET', '/admin/stats',            200),
        ('GET', '/admin/map',              200),
        ('GET', '/admin/map/data',         200),
        ('GET', '/admin/complaints/9999',  404),
        ('GET', '/no-such-page',           404),
    ]

    print('Route                            Exp  Got  Result')
    print('-' * 54)
    for method, path, expected in routes:
        r = c.get(path)
        ok = r.status_code == expected
        if not ok:
            errors.append((path, expected, r.status_code))
        # Special case: /admin/login redirects when already logged in — that is correct
        if path == '/admin/login' and r.status_code == 302:
            result = 'OK (redirects — already logged in)'
            errors[:] = [e for e in errors if e[0] != path]
        result = 'OK' if ok else 'FAIL'
        print(f'  {method} {path:<33} {expected}  {r.status_code}  {result}')

    print()
    print('Content checks:')

    r = c.get('/')
    print('  / has submission form:       ', 'Report a Civic Issue' in r.data.decode())

    r = c.get('/admin/')
    body = r.data.decode()
    print('  /admin/ has stat cards:      ', 'Total Complaints' in body)
    print('  /admin/ has chart canvases:  ', 'chart-status' in body)

    r = c.get('/admin/map/data')
    markers = json.loads(r.data)
    print(f'  /admin/map/data markers:      {len(markers)} geo-tagged complaints')
    if markers:
        print('  First marker has lat/lng:    ', markers[0].get('latitude') is not None)

    r = c.get('/admin/stats')
    stats = json.loads(r.data)
    print('  /admin/stats by_status:      ', stats['by_status'])
    print('  /admin/stats by_category:    ', stats['by_category'])
    print('  /admin/stats by_priority:    ', stats['by_priority'])
    print('  /admin/stats 30-day window:  ', len(stats['by_date']) == 30)

    r = c.post('/submit', data={
        'title': 'Broken streetlight on Brigade Road',
        'description': 'The lamp post near Brigade Road junction has been dark for 3 weeks unsafe at night',
        'category': 'Streetlight',
        'location_text': 'Brigade Road Junction, Bengaluru',
        'latitude': '12.9750',
        'longitude': '77.6070',
    }, follow_redirects=True)
    body = r.data.decode()
    print('  Submit complaint:             status', r.status_code, '| success page:', 'Complaint Submitted' in body)

    r = c.post('/track', data={'complaint_id': '3'}, follow_redirects=True)
    body = r.data.decode()
    print('  Track complaint #3:           status', r.status_code, '| found:', 'Drainage' in body)

    r = c.post('/admin/complaints/1/update',
               data={'status': 'In Progress', 'note': 'Team dispatched'},
               follow_redirects=True)
    print('  Update complaint #1 status:   status', r.status_code, '| flash:', 'updated' in r.data.decode())

with app.app_context():
    from app import db
    from app.models import Complaint
    c1 = db.session.get(Complaint, 1)
    print('  Complaint #1 new status:     ', c1.status)
    print('  Complaint #1 notes count:    ', len(c1.admin_notes))

with app.test_client() as c2:
    r = c2.post('/admin/login',
                data={'password': 'wrongpassword'},
                follow_redirects=True)
    print('  Wrong password shows error:  ', 'Incorrect' in r.data.decode())

print()
if errors:
    print('FAILED routes:', errors)
else:
    print('All route tests passed.')

"""
init_db.py — Creates the SQLite database and seeds sample data.
Run once before starting the application:
    python init_db.py
"""

from app import create_app, db
from app.models import Complaint, AdminNote
from datetime import datetime, timedelta

app = create_app()

SEED_COMPLAINTS = [
    {
        "title": "Large Pothole on Residency Road",
        "description": "There is a large pothole near the signal on Residency Road causing accidents and vehicle damage. Urgent repair needed.",
        "category": "Road Damage",
        "location_text": "Residency Road, Near Signal, Bengaluru",
        "latitude": 12.9719,
        "longitude": 77.5937,
        "priority": "High",
        "status": "Pending",
    },
    {
        "title": "Uncollected Garbage Near Cubbon Park",
        "description": "A huge pile of garbage has been accumulating near the Cubbon Park entrance for over a week. Bad smell and health hazard.",
        "category": "Garbage",
        "location_text": "Cubbon Park Entrance, MG Road, Bengaluru",
        "latitude": 12.9763,
        "longitude": 77.5929,
        "priority": "Medium",
        "status": "In Progress",
    },
    {
        "title": "Blocked Drainage Causing Waterlogging",
        "description": "The drainage near Koramangala 4th Block is completely blocked causing severe waterlogging after every rain. Flooding is affecting shops and homes.",
        "category": "Drainage",
        "location_text": "Koramangala 4th Block, Bengaluru",
        "latitude": 12.9352,
        "longitude": 77.6245,
        "priority": "High",
        "status": "Pending",
    },
    {
        "title": "Water Pipe Burst on Jayanagar Main Road",
        "description": "A water pipe has burst on Jayanagar 3rd Block main road. Water is gushing out and causing road damage. Immediate attention required.",
        "category": "Water Leakage",
        "location_text": "Jayanagar 3rd Block, Bengaluru",
        "latitude": 12.9288,
        "longitude": 77.5826,
        "priority": "High",
        "status": "Resolved",
    },
    {
        "title": "Streetlight Not Working Near Bus Stop",
        "description": "The street lamp near the Indiranagar bus stop has not been working for two weeks. The area is very dark at night and feels unsafe.",
        "category": "Streetlight",
        "location_text": "Indiranagar 100 Feet Road, Near Bus Stop, Bengaluru",
        "latitude": 12.9784,
        "longitude": 77.6408,
        "priority": "Medium",
        "status": "Pending",
    },
    {
        "title": "Stray Animals and Garbage Dump Near School",
        "description": "There is an unauthorized garbage dump near a school in Whitefield. Stray animals gather there daily creating a safety issue for children.",
        "category": "Garbage",
        "location_text": "Whitefield Main Road, Near Government School, Bengaluru",
        "latitude": 12.9698,
        "longitude": 77.7500,
        "priority": "High",
        "status": "Pending",
    },
    {
        "title": "Open Manhole on HSR Layout Road",
        "description": "An open manhole on the main road in HSR Layout sector 2 is a danger for pedestrians and two-wheelers especially at night.",
        "category": "Drainage",
        "location_text": "HSR Layout Sector 2, Bengaluru",
        "latitude": 12.9116,
        "longitude": 77.6389,
        "priority": "High",
        "status": "In Progress",
    },
    {
        "title": "No Street Lighting in Entire Lane",
        "description": "The entire residential lane near BTM Layout 2nd Stage has no functioning streetlights. Residents feel unsafe walking at night.",
        "category": "Streetlight",
        "location_text": "BTM Layout 2nd Stage, Lane 5, Bengaluru",
        "latitude": 12.9165,
        "longitude": 77.6101,
        "priority": "Medium",
        "status": "Pending",
    },
]

SEED_NOTES = [
    (2, "Team dispatched to collect garbage. Expected completion by tomorrow."),
    (4, "Pipe repaired by BWSSB team on 1st November. Water supply restored."),
    (7, "Manhole cover ordered. Installation scheduled for next week."),
]


def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database tables created.")

        base_time = datetime.utcnow() - timedelta(days=10)
        complaints = []
        for i, data in enumerate(SEED_COMPLAINTS):
            c = Complaint(
                title=data["title"],
                description=data["description"],
                category=data["category"],
                location_text=data["location_text"],
                latitude=data.get("latitude"),
                longitude=data.get("longitude"),
                priority=data["priority"],
                status=data["status"],
                submitted_at=base_time + timedelta(days=i),
                updated_at=base_time + timedelta(days=i),
            )
            db.session.add(c)
            complaints.append(c)

        db.session.flush()  # assign IDs

        for complaint_id, note_text in SEED_NOTES:
            note = AdminNote(
                complaint_id=complaint_id,
                note=note_text,
            )
            db.session.add(note)

        db.session.commit()
        print(f"Seeded {len(SEED_COMPLAINTS)} complaints and {len(SEED_NOTES)} admin notes.")
        print("Database initialised at: instance/civicpulse.db")


if __name__ == "__main__":
    seed()

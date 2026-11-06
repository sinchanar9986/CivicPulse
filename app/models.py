from datetime import datetime
from app import db


class Complaint(db.Model):
    __tablename__ = "complaints"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location_text = db.Column(db.String(300), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    priority = db.Column(db.String(10), nullable=False, default="Medium")
    status = db.Column(db.String(20), nullable=False, default="Pending")
    image_filename = db.Column(db.String(255), nullable=True)
    is_duplicate = db.Column(db.Boolean, default=False, nullable=False)
    duplicate_of_id = db.Column(db.Integer, db.ForeignKey("complaints.id"), nullable=True)
    similarity_score = db.Column(db.Float, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    admin_notes = db.relationship("AdminNote", backref="complaint", lazy=True, cascade="all, delete-orphan")
    duplicate_original = db.relationship("Complaint", remote_side=[id], foreign_keys=[duplicate_of_id])

    @staticmethod
    def valid_statuses():
        return ["Pending", "In Progress", "Resolved", "Archived"]

    @staticmethod
    def valid_categories():
        return ["Garbage", "Road Damage", "Drainage", "Water Leakage", "Streetlight", "Other"]

    @staticmethod
    def valid_priorities():
        return ["High", "Medium", "Low"]

    def __repr__(self):
        return f"<Complaint #{self.id} [{self.category}] {self.status!r}: {self.title[:40]}>"


class AdminNote(db.Model):
    __tablename__ = "admin_notes"

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaints.id"), nullable=False)
    note = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<AdminNote for complaint #{self.complaint_id}>"

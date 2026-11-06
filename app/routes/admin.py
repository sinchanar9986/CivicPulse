import json
from datetime import datetime, timedelta
from functools import wraps

import bcrypt
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session, current_app, jsonify)

from app import db
from app.models import Complaint, AdminNote

admin_bp = Blueprint("admin", __name__)


# ---- Auth helpers ----

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please log in to access the admin area.", "warning")
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        password = request.form.get("password", "")
        stored   = current_app.config["ADMIN_PASSWORD"]

        # Support both plain-text dev password and bcrypt hash
        try:
            match = bcrypt.checkpw(password.encode(), stored.encode())
        except Exception:
            match = (password == stored)

        if match:
            session["admin_logged_in"] = True
            session.permanent = True
            return redirect(url_for("admin.dashboard"))
        else:
            flash("Incorrect password. Please try again.", "error")

    return render_template("admin/login.html")


@admin_bp.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("citizen.index"))


# ---- Dashboard ----

@admin_bp.route("/")
@login_required
def dashboard():
    stats = {
        "total":       Complaint.query.count(),
        "pending":     Complaint.query.filter_by(status="Pending").count(),
        "in_progress": Complaint.query.filter_by(status="In Progress").count(),
        "resolved":    Complaint.query.filter_by(status="Resolved").count(),
    }
    recent = (Complaint.query
              .order_by(Complaint.submitted_at.desc())
              .limit(10)
              .all())
    return render_template("admin/dashboard.html", stats=stats, recent=recent)


# ---- Stats API (for Chart.js) ----

@admin_bp.route("/stats")
def stats():
    """Return JSON statistics for dashboard charts."""
    # By status
    by_status = {}
    for s in Complaint.valid_statuses():
        count = Complaint.query.filter_by(status=s).count()
        if count:
            by_status[s] = count

    # By category
    by_category = {}
    for cat in Complaint.valid_categories():
        count = Complaint.query.filter_by(category=cat).count()
        if count:
            by_category[cat] = count

    # By priority
    by_priority = {}
    for p in Complaint.valid_priorities():
        count = Complaint.query.filter_by(priority=p).count()
        if count:
            by_priority[p] = count

    # By date (last 30 days)
    by_date = {}
    today = datetime.utcnow().date()
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        label = day.strftime("%d %b")
        count = Complaint.query.filter(
            db.func.date(Complaint.submitted_at) == day.isoformat()
        ).count()
        by_date[label] = count

    return jsonify(
        by_status=by_status,
        by_category=by_category,
        by_priority=by_priority,
        by_date=by_date,
    )


# ---- Complaints list ----

@admin_bp.route("/complaints")
@login_required
def complaints_list():
    page     = request.args.get("page", 1, type=int)
    q        = request.args.get("q", "").strip()
    status   = request.args.get("status", "")
    category = request.args.get("category", "")
    priority = request.args.get("priority", "")

    query = Complaint.query

    if q:
        like = f"%{q}%"
        query = query.filter(
            (Complaint.title.ilike(like)) | (Complaint.description.ilike(like))
        )
    if status:
        query = query.filter_by(status=status)
    if category:
        query = query.filter_by(category=category)
    if priority:
        query = query.filter_by(priority=priority)

    pagination = (query
                  .order_by(Complaint.submitted_at.desc())
                  .paginate(page=page, per_page=20, error_out=False))

    filters = dict(q=q, status=status, category=category, priority=priority)

    return render_template(
        "admin/complaints.html",
        complaints=pagination.items,
        pagination=pagination,
        filters=filters,
        statuses=Complaint.valid_statuses(),
        categories=Complaint.valid_categories(),
        priorities=Complaint.valid_priorities(),
    )


# ---- Complaint detail ----

@admin_bp.route("/complaints/<int:complaint_id>")
@login_required
def complaint_detail(complaint_id):
    complaint = db.get_or_404(Complaint, complaint_id)
    return render_template(
        "admin/complaint_detail.html",
        complaint=complaint,
        statuses=Complaint.valid_statuses(),
    )


# ---- Update complaint ----

@admin_bp.route("/complaints/<int:complaint_id>/update", methods=["POST"])
@login_required
def update_complaint(complaint_id):
    complaint = db.get_or_404(Complaint, complaint_id)

    new_status = request.form.get("status", "").strip()
    note_text  = request.form.get("note", "").strip()

    if new_status in Complaint.valid_statuses():
        complaint.status = new_status
        complaint.updated_at = datetime.utcnow()

    if note_text:
        note = AdminNote(complaint_id=complaint.id, note=note_text)
        db.session.add(note)

    db.session.commit()
    flash("Complaint updated successfully.", "success")
    return redirect(url_for("admin.complaint_detail", complaint_id=complaint.id))


# ---- Archive complaint ----

@admin_bp.route("/complaints/<int:complaint_id>/archive")
@login_required
def archive_complaint(complaint_id):
    complaint = db.get_or_404(Complaint, complaint_id)
    complaint.status = "Archived"
    complaint.updated_at = datetime.utcnow()
    db.session.commit()
    flash(f"Complaint #{complaint.id} archived.", "info")
    return redirect(url_for("admin.complaints_list"))


# ---- Map view ----

@admin_bp.route("/map")
@login_required
def map_view():
    all_complaints = Complaint.query.filter(Complaint.status != "Archived").all()

    geo_complaints    = [c for c in all_complaints if c.latitude and c.longitude]
    no_coords         = [c for c in all_complaints if not c.latitude or not c.longitude]

    complaints_json = json.dumps([{
        "id":            c.id,
        "title":         c.title,
        "category":      c.category,
        "location_text": c.location_text,
        "status":        c.status,
        "priority":      c.priority,
        "latitude":      c.latitude,
        "longitude":     c.longitude,
    } for c in geo_complaints])

    return render_template(
        "admin/map.html",
        complaints=geo_complaints,
        complaints_json=complaints_json,
        no_coords_complaints=no_coords,
    )


# ---- Map data API ----

@admin_bp.route("/map/data")
@login_required
def map_data():
    complaints = Complaint.query.filter(
        Complaint.status != "Archived",
        Complaint.latitude.isnot(None),
        Complaint.longitude.isnot(None),
    ).all()
    return jsonify([{
        "id":            c.id,
        "title":         c.title,
        "category":      c.category,
        "location_text": c.location_text,
        "status":        c.status,
        "priority":      c.priority,
        "latitude":      c.latitude,
        "longitude":     c.longitude,
    } for c in complaints])

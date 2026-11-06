import os
import uuid

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, current_app)
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Optional

from app import db
from app.models import Complaint
from app.ai.classifier import classify
from app.ai.duplicate import find_duplicate
from app.ai.priority import assign_priority

citizen_bp = Blueprint("citizen", __name__)

CATEGORIES = ["Garbage", "Road Damage", "Drainage", "Water Leakage", "Streetlight", "Other"]


class ComplaintForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[DataRequired(), Length(min=5, max=200, message="Title must be 5–200 characters.")],
    )
    description = TextAreaField(
        "Description",
        validators=[DataRequired(), Length(min=20, max=2000, message="Description must be 20–2000 characters.")],
    )
    category = SelectField(
        "Category",
        choices=[("", "-- Select a category --")] + [(c, c) for c in CATEGORIES],
        validators=[DataRequired(message="Please select a category.")],
    )
    location_text = StringField(
        "Location",
        validators=[DataRequired(message="Please enter or pick a location."), Length(max=300)],
    )
    latitude  = HiddenField("Latitude",  validators=[Optional()])
    longitude = HiddenField("Longitude", validators=[Optional()])
    image = FileField(
        "Photo",
        validators=[
            Optional(),
            FileAllowed(["jpg", "jpeg", "png", "gif"], "Only JPG, PNG or GIF files are allowed."),
        ],
    )


def _save_image(file) -> str | None:
    """Save uploaded image; return filename or None."""
    if not file or not file.filename:
        return None
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in current_app.config["ALLOWED_EXTENSIONS"]:
        return None
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(path)
    return filename


@citizen_bp.route("/")
def index():
    form = ComplaintForm()
    return render_template("citizen/index.html", form=form)


@citizen_bp.route("/submit", methods=["POST"])
def submit():
    form = ComplaintForm()
    if not form.validate_on_submit():
        return render_template("citizen/index.html", form=form)

    title       = form.title.data.strip()
    description = form.description.data.strip()
    category    = form.category.data

    # --- AI pipeline ---
    # 1. Auto-classify if category left as default (shouldn't happen with required field,
    #    but also auto-confirm via AI for categorization accuracy)
    ai_category = classify(title, description)
    # Use user-selected category; AI category stored for reference
    final_category = category if category else ai_category

    # 2. Priority
    priority = assign_priority(final_category, description)

    # 3. Duplicate detection (check against non-archived complaints)
    existing = Complaint.query.filter(Complaint.status != "Archived").all()
    is_dup, dup_id, sim_score = find_duplicate(
        title, description, existing,
        threshold=current_app.config["DUPLICATE_THRESHOLD"],
    )

    # 4. Save image
    image_filename = _save_image(form.image.data)

    # 5. Parse lat/lng
    try:
        lat = float(form.latitude.data) if form.latitude.data else None
        lng = float(form.longitude.data) if form.longitude.data else None
    except (ValueError, TypeError):
        lat = lng = None

    # 6. Persist
    complaint = Complaint(
        title=title,
        description=description,
        category=final_category,
        location_text=form.location_text.data.strip(),
        latitude=lat,
        longitude=lng,
        priority=priority,
        status="Pending",
        image_filename=image_filename,
        is_duplicate=is_dup,
        duplicate_of_id=dup_id if is_dup else None,
        similarity_score=sim_score if is_dup else None,
    )
    db.session.add(complaint)
    db.session.commit()

    return redirect(url_for("citizen.success", complaint_id=complaint.id))


@citizen_bp.route("/success/<int:complaint_id>")
def success(complaint_id):
    complaint = db.get_or_404(Complaint, complaint_id)
    return render_template("citizen/success.html", complaint=complaint)


@citizen_bp.route("/track", methods=["GET", "POST"])
def track():
    complaint   = None
    searched    = False
    searched_id = None

    if request.method == "POST":
        searched = True
        try:
            searched_id = int(request.form.get("complaint_id", 0))
            complaint = db.session.get(Complaint, searched_id)
        except (ValueError, TypeError):
            pass

    return render_template(
        "citizen/track.html",
        complaint=complaint,
        searched=searched,
        searched_id=searched_id,
    )

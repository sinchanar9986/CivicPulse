import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from config import DevelopmentConfig

db = SQLAlchemy()
csrf = CSRFProtect()


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Ensure the upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.routes.citizen import citizen_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(citizen_bp, url_prefix="/")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("500.html"), 500

    @app.errorhandler(413)
    def too_large(e):
        from flask import flash, redirect, url_for
        flash("File is too large. Maximum allowed size is 5 MB.", "error")
        return redirect(url_for("citizen.index"))

    return app

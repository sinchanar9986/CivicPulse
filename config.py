import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("CIVICPULSE_SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = "sqlite:///civicpulse.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}
    ADMIN_PASSWORD = os.environ.get("CIVICPULSE_ADMIN_PASSWORD", "admin123")
    MAP_DEFAULT_LAT = 12.9716
    MAP_DEFAULT_LNG = 77.5946
    DUPLICATE_THRESHOLD = 0.75


class DevelopmentConfig(Config):
    DEBUG = True

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'finance.db'}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = UPLOAD_FOLDER
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB limit per request

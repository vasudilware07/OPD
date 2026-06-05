"""Application configuration loaded from environment variables."""
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "plum_opd")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

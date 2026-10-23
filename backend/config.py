from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent

ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    from dotenv import load_dotenv
    load_dotenv(ENV_PATH)

CHARGEBEE_API_KEY = os.getenv("CHARGEBEE_API_KEY", "")
CHARGEBEE_SITE = os.getenv("CHARGEBEE_SITE", "")
DEMO_MODE = os.getenv("DEMO_MODE", "true").strip().lower() == "true"
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5001"))
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

"""Entry point: uvicorn api.main:app --reload (from the repo root). Settings come from .env."""

import os

from dotenv import load_dotenv

from .app import create_app

load_dotenv()

app = create_app(
    database_url=os.getenv("DATABASE_URL") or "sqlite:///rebound.db",
    frontend_url=os.getenv("FRONTEND_URL") or None,
    demo_mode=os.getenv("DEMO_MODE", "").strip().lower() == "true",
)

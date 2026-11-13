"""Entry point: uvicorn api.main:app --reload (from the repo root). Settings come from .env."""

import os

from dotenv import load_dotenv

from .app import create_app

load_dotenv()


def _flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() == "true"


app = create_app(
    database_url=os.getenv("DATABASE_URL") or "sqlite:///rebound.db",
    frontend_url=os.getenv("FRONTEND_URL") or None,
    demo_mode=_flag("DEMO_MODE"),
    dev_mode=_flag("DEV_MODE"),
)

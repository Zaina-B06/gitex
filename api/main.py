"""Entry point: uvicorn api.main:app --reload (from the repo root). Settings come from .env."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from .app import create_app

load_dotenv()

# Show which check-in classifier answered ("llm" | "keywords") in the server terminal; never sent to users.
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("%(levelname)s:     %(message)s"))
_checkin_log = logging.getLogger("rebound.checkin")
_checkin_log.addHandler(_handler)
_checkin_log.setLevel(logging.INFO)


def _flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() == "true"


app = create_app(
    database_url=os.getenv("DATABASE_URL") or "sqlite:///rebound.db",
    frontend_url=os.getenv("FRONTEND_URL") or None,
    demo_mode=_flag("DEMO_MODE"),
    dev_mode=_flag("DEV_MODE"),
    demo_key=os.getenv("DEMO_KEY") or None,
    org_key=os.getenv("ORG_KEY") or None,
    dashboard_path=Path(__file__).resolve().parents[1] / "docs" / "results" / "dashboard.json",
)

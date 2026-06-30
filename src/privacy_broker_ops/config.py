from __future__ import annotations

from pathlib import Path

APP_DIR = Path.cwd()
DEFAULT_DB_PATH = APP_DIR / "privacy_broker_ops.db"
DEFAULT_BROKERS_PATH = APP_DIR / "data" / "brokers.yaml"
DEFAULT_PERSON_PATH = APP_DIR / "data" / "person.yaml"

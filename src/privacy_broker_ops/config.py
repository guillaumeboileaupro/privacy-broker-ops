from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

APP_NAME = "privacy-broker-ops"
DEFAULT_PROFILE = "default"
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
DEFAULT_BROKERS_PATH = DATA_DIR / "brokers.yaml"
DEFAULT_PERSON_EXAMPLE_PATH = DATA_DIR / "person.example.yaml"


def profile_data_home() -> Path:
    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home)
    return Path.home() / ".local" / "share"


def validate_profile_name(profile: str) -> str:
    cleaned = profile.strip()
    if not cleaned:
        raise ValueError("Le nom de profil ne peut pas etre vide.")
    if cleaned in {".", ".."} or "/" in cleaned:
        raise ValueError(f"Nom de profil invalide: {profile}")
    return cleaned


@dataclass(frozen=True)
class ProfilePaths:
    profile: str
    root: Path
    db_path: Path
    person_path: Path
    mail_dir: Path
    evidence_dir: Path
    exports_dir: Path

    @property
    def requests_dir(self) -> Path:
        return self.exports_dir / "requests"

    @property
    def tracker_path(self) -> Path:
        return self.exports_dir / "tracker.csv"

    def ensure_dirs(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.mail_dir.mkdir(parents=True, exist_ok=True)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)


def resolve_profile_paths(
    profile: str = DEFAULT_PROFILE,
    *,
    data_home: Path | None = None,
) -> ProfilePaths:
    profile_name = validate_profile_name(profile)
    base_dir = (data_home or profile_data_home()) / APP_NAME / "profiles" / profile_name
    return ProfilePaths(
        profile=profile_name,
        root=base_dir,
        db_path=base_dir / "privacy_broker_ops.db",
        person_path=base_dir / "person.yaml",
        mail_dir=base_dir / "mail",
        evidence_dir=base_dir / "evidence",
        exports_dir=base_dir / "exports",
    )

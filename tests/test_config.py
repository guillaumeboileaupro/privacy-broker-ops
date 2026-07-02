from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from privacy_broker_ops.cli import app
from privacy_broker_ops.config import DEFAULT_PROFILE, resolve_profile_paths

runner = CliRunner()


def test_resolve_default_profile_paths(tmp_path: Path) -> None:
    paths = resolve_profile_paths(data_home=tmp_path)

    assert paths.profile == DEFAULT_PROFILE
    assert paths.root == tmp_path / "privacy-broker-ops" / "profiles" / DEFAULT_PROFILE
    assert paths.db_path == paths.root / "privacy_broker_ops.db"
    assert paths.person_path == paths.root / "person.yaml"
    assert paths.mail_dir == paths.root / "mail"
    assert paths.evidence_dir == paths.root / "evidence"
    assert paths.exports_dir == paths.root / "exports"


def test_resolve_named_profile_paths(tmp_path: Path) -> None:
    paths = resolve_profile_paths("guillaume", data_home=tmp_path)

    assert paths.profile == "guillaume"
    assert paths.root == tmp_path / "privacy-broker-ops" / "profiles" / "guillaume"


def test_init_creates_profile_directories(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0
    paths = resolve_profile_paths(data_home=tmp_path)
    assert paths.root.is_dir()
    assert paths.mail_dir.is_dir()
    assert paths.evidence_dir.is_dir()
    assert paths.exports_dir.is_dir()
    assert paths.db_path.exists()


def test_init_named_profile_creates_named_database(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

    result = runner.invoke(app, ["init", "--profile", "guillaume"])

    assert result.exit_code == 0
    paths = resolve_profile_paths("guillaume", data_home=tmp_path)
    assert paths.db_path.exists()
    assert not resolve_profile_paths(data_home=tmp_path).db_path.exists()


def test_exposure_add_accepts_temporary_db(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"

    result = runner.invoke(
        app,
        [
            "exposure",
            "add",
            "--broker",
            "idcrawl",
            "--url",
            "https://example.com/profile",
            "--db",
            str(db_path),
        ],
    )

    assert result.exit_code == 0
    assert db_path.exists()

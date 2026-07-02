from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import uvicorn
from fastapi import HTTPException
from typer.testing import CliRunner

from privacy_broker_ops.cli import app
from privacy_broker_ops.config import resolve_profile_paths
from privacy_broker_ops.dashboard import create_app
from privacy_broker_ops.models import ExposureCreate, ExposureStatus
from privacy_broker_ops.repository import Repository

runner = CliRunner()


def find_endpoint(app_object: object, path: str, method: str):
    for route in app_object.routes:
        if getattr(route, "path", None) == path and method in getattr(route, "methods", set()):
            return route.endpoint
    raise AssertionError(f"Route introuvable: {method} {path}")


def setup_profile(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    init_result = runner.invoke(app, ["init", "--profile", "guillaume"])
    assert init_result.exit_code == 0
    paths = resolve_profile_paths("guillaume", data_home=tmp_path)
    paths.person_path.write_text(
        "full_name: Guillaume Test\nemail: secret@example.com\n",
        encoding="utf-8",
    )
    return paths.db_path


def seed_dashboard_data(db_path: Path) -> Repository:
    repo = Repository(db_path)
    repo.init()
    first_id = repo.add_exposure(
        ExposureCreate(
            broker_id="idcrawl",
            url="https://example.com/profile/1",
            status=ExposureStatus.ENVOYE,
            note="Relance attendue",
        )
    )
    second_id = repo.add_exposure(
        ExposureCreate(
            broker_id="idcrawl",
            url="https://example.com/profile/2",
            status=ExposureStatus.CONFIRME,
            note="Visible",
        )
    )
    with repo.connect() as con:
        con.execute(
            "UPDATE exposures SET last_contact_at = ? WHERE id = ?",
            ((datetime.now(UTC) - timedelta(days=31)).replace(microsecond=0).isoformat(), first_id),
        )
        con.execute(
            """
            INSERT INTO mail_events (
                exposure_id, broker_id, direction, kind, subject, from_address, to_address,
                sent_at, received_at, status, eml_path, body_excerpt, sha256, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                second_id,
                "idcrawl",
                "INBOUND",
                "RESPONSE",
                "Re: Demande RGPD",
                "privacy@example.com",
                "secret@example.com",
                None,
                "2026-07-01T10:00:00+00:00",
                "received",
                str(db_path.parent / "mail" / "inbox" / "sample.txt"),
                "Extrait court visible",
                "abcdef1234567890",
                "2026-07-01T10:00:00+00:00",
            ),
        )
    return repo


def test_dashboard_cli_uses_localhost_by_default(monkeypatch, tmp_path: Path) -> None:
    setup_profile(tmp_path, monkeypatch)
    calls: dict[str, object] = {}

    def fake_run(app_target: object, host: str, port: int, reload: bool) -> None:
        calls["app"] = app_target
        calls["host"] = host
        calls["port"] = port
        calls["reload"] = reload

    monkeypatch.setattr(uvicorn, "run", fake_run)

    result = runner.invoke(app, ["dashboard", "--profile", "guillaume"])

    assert result.exit_code == 0
    assert calls["host"] == "127.0.0.1"
    assert calls["port"] == 8080
    assert calls["reload"] is False


def test_dashboard_home_shows_counters_and_broker_counts(tmp_path: Path, monkeypatch) -> None:
    db_path = setup_profile(tmp_path, monkeypatch)
    seed_dashboard_data(db_path)
    dashboard_app = create_app(db_path, profile="guillaume")

    response = find_endpoint(dashboard_app, "/", "GET")()

    assert "Total" in response
    assert ">2<" in response
    assert "ENVOYE" in response
    assert "CONFIRME" in response
    assert "Compteurs par broker" in response
    assert "idcrawl" in response


def test_dashboard_readonly_blocks_write_actions(tmp_path: Path, monkeypatch) -> None:
    db_path = setup_profile(tmp_path, monkeypatch)
    seed_dashboard_data(db_path)
    dashboard_app = create_app(db_path, profile="guillaume", readonly=True)

    endpoint = find_endpoint(dashboard_app, "/actions/export-csv", "POST")
    try:
        endpoint()
    except HTTPException as exc:
        assert exc.status_code == 403
        assert "lecture seule" in exc.detail.lower()
    else:
        raise AssertionError("Le mode readonly aurait du bloquer l'export.")

    exports_dir = db_path.parent / "exports"
    assert not (exports_dir / "tracker.csv").exists()


def test_dashboard_detail_hides_secret_values(tmp_path: Path, monkeypatch) -> None:
    db_path = setup_profile(tmp_path, monkeypatch)
    seed_dashboard_data(db_path)
    dashboard_app = create_app(db_path, profile="guillaume")

    response = find_endpoint(dashboard_app, "/exposures/{exposure_id}", "GET")(2)

    assert "Re: Demande RGPD" in response
    assert "Extrait court visible" in response
    assert "secret@example.com" not in response
    assert "full_name" not in response

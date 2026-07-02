from __future__ import annotations

import hashlib
from pathlib import Path

from typer.testing import CliRunner

from privacy_broker_ops.cli import app
from privacy_broker_ops.config import resolve_profile_paths
from privacy_broker_ops.repository import Repository

runner = CliRunner()


def test_mail_import_txt_stores_file_and_hash(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    source = tmp_path / "reply.txt"
    source.write_text("Bonjour,\nNous avons bien recu votre demande RGPD.", encoding="utf-8")

    init_result = runner.invoke(app, ["init"])
    assert init_result.exit_code == 0

    exposure_result = runner.invoke(
        app,
        [
            "exposure",
            "add",
            "--broker",
            "idcrawl",
            "--url",
            "https://example.com/profile",
        ],
    )
    assert exposure_result.exit_code == 0

    result = runner.invoke(
        app,
        [
            "mail",
            "import",
            "--file",
            str(source),
            "--exposure-id",
            "1",
        ],
    )

    assert result.exit_code == 0
    paths = resolve_profile_paths(data_home=tmp_path)
    stored_files = list((paths.mail_dir / "inbox").glob("*.txt"))
    assert len(stored_files) == 1
    expected_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    assert stored_files[0].name == f"{expected_hash}.txt"

    repo = Repository(paths.db_path)
    events = repo.list_mail_events()
    assert len(events) == 1
    assert events[0].sha256 == expected_hash
    assert "Bonjour" in events[0].body_excerpt


def test_mail_import_minimal_eml_extracts_headers(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    source = tmp_path / "response.eml"
    source.write_text(
        (
            "From: privacy@example.com\n"
            "To: guillaume@example.com\n"
            "Subject: Re: Demande RGPD\n"
            "Date: Tue, 01 Jul 2026 10:00:00 +0000\n"
            "\n"
            "Votre demande a ete prise en compte.\n"
        ),
        encoding="utf-8",
    )

    init_result = runner.invoke(app, ["init", "--profile", "guillaume"])
    assert init_result.exit_code == 0

    exposure_result = runner.invoke(
        app,
        [
            "exposure",
            "add",
            "--profile",
            "guillaume",
            "--broker",
            "idcrawl",
            "--url",
            "https://example.com/profile",
        ],
    )
    assert exposure_result.exit_code == 0

    result = runner.invoke(
        app,
        [
            "mail",
            "import",
            "--profile",
            "guillaume",
            "--file",
            str(source),
            "--exposure-id",
            "1",
        ],
    )

    assert result.exit_code == 0
    paths = resolve_profile_paths("guillaume", data_home=tmp_path)
    events = Repository(paths.db_path).list_mail_events()
    assert len(events) == 1
    assert events[0].subject == "Re: Demande RGPD"
    assert events[0].from_address == "privacy@example.com"
    assert events[0].to_address == "guillaume@example.com"
    assert events[0].kind.value == "RESPONSE"
    assert events[0].received_at == "2026-07-01T10:00:00+00:00"


def test_mail_list_uses_temporary_database(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    source = tmp_path / "mail.txt"
    source.write_text("Message de test", encoding="utf-8")

    exposure_result = runner.invoke(
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
    assert exposure_result.exit_code == 0

    import_result = runner.invoke(
        app,
        [
            "mail",
            "import",
            "--file",
            str(source),
            "--exposure-id",
            "1",
            "--db",
            str(db_path),
        ],
    )
    assert import_result.exit_code == 0

    result = runner.invoke(app, ["mail", "list", "--db", str(db_path)])

    assert result.exit_code == 0
    assert "Mail events" in result.stdout

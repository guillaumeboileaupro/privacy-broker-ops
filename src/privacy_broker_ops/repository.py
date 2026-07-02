from __future__ import annotations

import csv
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from .models import Exposure, ExposureCreate, ExposureStatus, MailEvent, MailEventCreate

SCHEMA = """
CREATE TABLE IF NOT EXISTS exposures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    broker_id TEXT NOT NULL,
    url TEXT NOT NULL,
    status TEXT NOT NULL,
    data_type TEXT NOT NULL DEFAULT '',
    note TEXT NOT NULL DEFAULT '',
    discovered_at TEXT NOT NULL,
    last_contact_at TEXT
);

CREATE TABLE IF NOT EXISTS mail_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exposure_id INTEGER NOT NULL,
    broker_id TEXT NOT NULL,
    direction TEXT NOT NULL,
    kind TEXT NOT NULL,
    subject TEXT NOT NULL,
    from_address TEXT NOT NULL DEFAULT '',
    to_address TEXT NOT NULL DEFAULT '',
    sent_at TEXT,
    received_at TEXT,
    status TEXT NOT NULL DEFAULT '',
    eml_path TEXT NOT NULL,
    body_excerpt TEXT NOT NULL DEFAULT '',
    sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(exposure_id) REFERENCES exposures(id)
);
"""


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


class Repository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def init(self) -> None:
        with self.connect() as con:
            con.executescript(SCHEMA)

    def add_exposure(self, item: ExposureCreate) -> int:
        with self.connect() as con:
            cur = con.execute(
                """
                INSERT INTO exposures (broker_id, url, status, data_type, note, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (item.broker_id, item.url, item.status.value, item.data_type, item.note, utc_now()),
            )
            return int(cur.lastrowid)

    def list_exposures(self) -> list[Exposure]:
        with self.connect() as con:
            rows = con.execute("SELECT * FROM exposures ORDER BY id DESC").fetchall()
        return [self._row_to_exposure(row) for row in rows]

    def get_exposure(self, exposure_id: int) -> Exposure:
        with self.connect() as con:
            row = con.execute("SELECT * FROM exposures WHERE id = ?", (exposure_id,)).fetchone()
        if row is None:
            raise ValueError(f"Exposure introuvable: {exposure_id}")
        return self._row_to_exposure(row)

    def mark_prepared(self, exposure_id: int) -> None:
        self.update_status(exposure_id, ExposureStatus.DEMANDE_PREPAREE)

    def mark_sent(self, exposure_id: int) -> None:
        with self.connect() as con:
            con.execute(
                "UPDATE exposures SET status = ?, last_contact_at = ? WHERE id = ?",
                (ExposureStatus.ENVOYE.value, utc_now(), exposure_id),
            )

    def update_status(self, exposure_id: int, status: ExposureStatus) -> None:
        with self.connect() as con:
            con.execute("UPDATE exposures SET status = ? WHERE id = ?", (status.value, exposure_id))

    def export_csv(self, out: Path) -> None:
        out.parent.mkdir(parents=True, exist_ok=True)
        rows = self.list_exposures()
        with out.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id",
                "broker_id",
                "url",
                "status",
                "data_type",
                "discovered_at",
                "last_contact_at",
                "note",
            ])
            for row in rows:
                writer.writerow([
                    row.id,
                    row.broker_id,
                    row.url,
                    row.status.value,
                    row.data_type,
                    row.discovered_at,
                    row.last_contact_at or "",
                    row.note,
                ])

    def add_mail_event(self, item: MailEventCreate) -> int:
        with self.connect() as con:
            cur = con.execute(
                """
                INSERT INTO mail_events (
                    exposure_id,
                    broker_id,
                    direction,
                    kind,
                    subject,
                    from_address,
                    to_address,
                    sent_at,
                    received_at,
                    status,
                    eml_path,
                    body_excerpt,
                    sha256,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.exposure_id,
                    item.broker_id,
                    item.direction.value,
                    item.kind.value,
                    item.subject,
                    item.from_address,
                    item.to_address,
                    item.sent_at,
                    item.received_at,
                    item.status,
                    item.eml_path,
                    item.body_excerpt,
                    item.sha256,
                    utc_now(),
                ),
            )
            return int(cur.lastrowid)

    def list_mail_events(self, exposure_id: int | None = None) -> list[MailEvent]:
        with self.connect() as con:
            if exposure_id is None:
                rows = con.execute("SELECT * FROM mail_events ORDER BY id DESC").fetchall()
            else:
                rows = con.execute(
                    "SELECT * FROM mail_events WHERE exposure_id = ? ORDER BY id DESC",
                    (exposure_id,),
                ).fetchall()
        return [self._row_to_mail_event(row) for row in rows]

    @staticmethod
    def _row_to_exposure(row: sqlite3.Row) -> Exposure:
        return Exposure(
            id=int(row["id"]),
            broker_id=str(row["broker_id"]),
            url=str(row["url"]),
            status=ExposureStatus(str(row["status"])),
            data_type=str(row["data_type"]),
            note=str(row["note"]),
            discovered_at=str(row["discovered_at"]),
            last_contact_at=row["last_contact_at"],
        )

    @staticmethod
    def _row_to_mail_event(row: sqlite3.Row) -> MailEvent:
        return MailEvent.model_validate(dict(row))
